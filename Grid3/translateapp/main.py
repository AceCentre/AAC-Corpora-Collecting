import streamlit as st
import xml.etree.ElementTree as ET
from deep_translator import GoogleTranslator, MicrosoftTranslator, DeeplTranslator
import zipfile
import os
from io import BytesIO
import tempfile
import shutil
import time
import datetime

translation_cache = {}


if "translation_cache" not in st.session_state:
    st.session_state["translation_cache"] = {}

def process_and_translate_xml(file, tool, source_lang, target_lang, api_key=None, region=None, tweak_xml=False, debug_mode=False, rate_limit_enabled=True):
    try:
        tree = ET.parse(file)
        root = tree.getroot()

        # Collect all translatable texts
        translatable_texts = []
        elements_to_translate = []

        for element in root.iter():
            if element.text and element.text.strip():
                translatable_texts.append(element.text)
                elements_to_translate.append(element)

        # Perform batch translation with caching
        translated_texts = []
        for text in translatable_texts:
            if text in st.session_state["translation_cache"]:
                # Use cached translation
                translated_texts.append(st.session_state["translation_cache"][text])
                if debug_mode:
                    st.write(f"Cache hit: '{text}' -> '{st.session_state['translation_cache'][text]}'")
            else:
                # Add to list for API translation
                translated_texts.append(None)

        # Translate only uncached texts
        texts_to_translate = [text for text, translated in zip(translatable_texts, translated_texts) if translated is None]
        if texts_to_translate:
            new_translations = translate_text(texts_to_translate, tool, source_lang, target_lang, api_key, region, rate_limit_enabled)
            for text, translation in zip(texts_to_translate, new_translations):
                st.session_state["translation_cache"][text] = translation  # Cache the new translation
                # Update the respective entry in the translated_texts list
                translated_texts[translatable_texts.index(text)] = translation
                if debug_mode:
                    st.write(f"Translated: '{text}' -> '{translation}'")

        # Update XML with translated text
        for element, translated in zip(elements_to_translate, translated_texts):
            if tweak_xml:
                element.text = wrap_in_cdata(translated.strip())
            else:
                element.text = translated

        # Save modified XML
        translated_xml = BytesIO()
        tree.write(translated_xml, encoding="utf-8", xml_declaration=True)
        return translated_xml
    except Exception as e:
        st.error(f"Error processing XML: {e}")
        return None
    
# For some languages we may need to do this
def wrap_in_cdata(text):
    return f"<![CDATA[{text}]]>"


# Function to get supported languages
def get_supported_languages(tool, api_key=None):
    try:
        if tool == "Google":
            return GoogleTranslator().get_supported_languages()
        elif tool == "Microsoft":
            if not api_key:
                return []
            return MicrosoftTranslator(api_key=api_key).get_supported_languages()
        elif tool == "DeepL":
            if not api_key:
                return []
            return DeeplTranslator(api_key=api_key).get_supported_languages()
    except Exception as e:
        st.error(f"Error fetching supported languages: {e}")
        return []

# Function to translate text
def translate_text(text_list, tool, source_lang, target_lang, api_key=None, region=None, rate_limit_enabled=False):
    try:
        if tool == "Google":
            if rate_limit_enabled:
                batch_size = 5  # Google allows 5 requests per second
                translated_texts = []
                for i in range(0, len(text_list), batch_size):
                    batch = text_list[i:i + batch_size]
                    translated_texts.extend(GoogleTranslator(source=source_lang, target=target_lang).translate_batch(batch))
                    time.sleep(1)  # Pause for 1 second after processing each batch
                return translated_texts
            else:
                return GoogleTranslator(source=source_lang, target=target_lang).translate_batch(text_list)
        elif tool == "Microsoft":
            if api_key and region:
                translator = MicrosoftTranslator(api_key=api_key, source=source_lang, target=target_lang, region=region)
                return translator.translate_batch(text_list)
            else:
                raise ValueError("Microsoft Translator requires both api_key and region.")
        elif tool == "DeepL":
            if api_key:
                translator = DeeplTranslator(api_key=api_key, source=source_lang, target=target_lang)
                return translator.translate_batch(text_list)
    except Exception as e:
        st.error(f"Translation error: {e}")
        return text_list
    
# Streamlit app
st.title("Gridset Translator")
st.markdown(
    """
    Welcome to the **Gridset Translator**, a tool designed to translate Gridset files for 
    [Grid 3 software](http://thinksmartbox.com/grid3). **Note: Please dont rely on this! This may be useful to get you started and will definitely be useful for phrases but for core word vocabulary systems be very wary of it!!** 

    ### Related Tools
    - [AAC Keyboard Maker](https://aackeyboardmaker.streamlit.app/): Create custom keyboards for Grid 3 in various languages.
    - [TTS Voices Available](https://ttsvoicesavailable.streamlit.app/): Check if Text-to-Speech (TTS) is supported in your desired language.
    - [AAC Speak Helper](https://docs.acecentre.org.uk/products/aac-speak-helper-tool): A tool to work with Windows AAC Softwre to provide additional languages for TTS and translation

    Upload your `.gridset` file, select your translation settings, and download the updated file with ease!
    """
)


#rate_limit = st.checkbox("Enable Rate Limiting for Google Translator (Avoid API Errors)", value=True)
rate_limit = True
# Select translation tool
translation_tool = st.selectbox("Select Translation Tool", ["Google", "Microsoft", "DeepL"])
region = None

# API Key input for paid tools
if translation_tool in ["Microsoft", "DeepL"]:
    st.markdown("**Note:** The API key will not be cached or stored.")
    if translation_tool == "Microsoft":
        api_key = st.text_input("Enter your Microsoft Translator API Key", type="password")
        region = st.text_input("Enter your Microsoft Translator Region", value="uksouth")
    else:
        api_key = None
        region = None
else:
    api_key = None

# Fetch supported languages dynamically
languages = get_supported_languages(translation_tool, api_key)

if languages:
    source_lang = st.selectbox("Source Language", options=languages, index=languages.index("english"))
    target_lang = st.selectbox("Target Language", options=languages, index=languages.index("spanish"))
else:
    st.error("Failed to fetch supported languages. Please check your API key or connection.")

# File upload
uploaded_file = st.file_uploader("Upload a Gridset file (.gridset)", type=["gridset"])
tweak_xml = st.checkbox("Tweak final Gridset for Better Language support (only use if it failed first time!)", value=False)
debug_mode = st.checkbox("Enable Debug Output", value=False)

if uploaded_file:
    # Manage temporary directory and cache
    if "last_uploaded_file" not in st.session_state or st.session_state["last_uploaded_file"] != uploaded_file.name:
        # Remove previous temp directory if a new file is uploaded
        if "temp_dir" in st.session_state and st.session_state["temp_dir"]:
            shutil.rmtree(st.session_state["temp_dir"].name, ignore_errors=True)
        # Create a new temp directory and reset cache
        st.session_state["temp_dir"] = tempfile.TemporaryDirectory()
        st.session_state["translation_cache"] = {}
        st.session_state["last_uploaded_file"] = uploaded_file.name

    temp_dir = st.session_state["temp_dir"].name

    # Extract uploaded file to temp_dir
    try:
        with zipfile.ZipFile(uploaded_file, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
        st.write("Files successfully extracted.")
    except Exception as e:
        st.error(f"Error extracting .gridset file: {e}")
        st.stop()

    # Count total XML files for progress bar
    total_files = sum(1 for _, _, files in os.walk(temp_dir) for f in files if f.endswith(".xml"))
    if total_files == 0:
        st.error("No XML files found in the uploaded gridset.")
        st.stop()

    # Initialize progress bar
    progress_bar = st.progress(0)
    progress_text = st.empty()  # Placeholder for progress text
    current_progress = 0

    # Record start time
    start_time = time.time()
    

    # Create ZIP file for translated content
    output_zip = BytesIO()
    with zipfile.ZipFile(output_zip, "w") as output_zip_ref:
        for root, _, files in os.walk(temp_dir):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                relative_path = os.path.relpath(file_path, temp_dir)

                # Process only XML files in the "Grids/" directory
                if relative_path.startswith("Grids/") and file_name.endswith(".xml"):
                    try:
                        if debug_mode:
                            st.write(f"Translating: {file_name}")
                        translated_xml = process_and_translate_xml(
                            file_path,
                            translation_tool,
                            source_lang,
                            target_lang,
                            api_key,
                            region,
                            tweak_xml=tweak_xml,
                            debug_mode=debug_mode,
                            rate_limit_enabled=rate_limit
                        )
                        if translated_xml:
                            output_zip_ref.writestr(relative_path, translated_xml.read())
                        else:
                            st.error(f"Failed to translate: {file_name}")
                    except Exception as e:
                        st.error(f"Error translating file {file_name}: {e}")
                else:
                    # Copy non-XML files directly
                    with open(file_path, "rb") as f:
                        output_zip_ref.writestr(relative_path, f.read())

                # Update progress bar
                current_progress += 1
                progress_bar.progress(int((current_progress / total_files) * 100))

                # Calculate elapsed time and ETA
                elapsed_time = time.time() - start_time
                avg_time_per_file = elapsed_time / current_progress if current_progress > 0 else 0
                remaining_files = total_files - current_progress
                estimated_time_remaining = remaining_files * avg_time_per_file
                eta = datetime.timedelta(seconds=int(estimated_time_remaining))

                # Update progress text
                progress_text.text(
                    f"Processed {current_progress}/{total_files} files. "
                    f"Elapsed: {datetime.timedelta(seconds=int(elapsed_time))}, "
                    f"ETA: {eta}."
                )

    # Provide the translated gridset for download
    if output_zip.tell() > 0:
        st.success("Translation complete!")
        output_zip.seek(0)
        translated_filename = f"{os.path.splitext(uploaded_file.name)[0]}-{target_lang}.gridset"
        st.download_button(
            label="Download Translated Gridset",
            data=output_zip,
            file_name=translated_filename,
            mime="application/zip",
        )
    else:
        st.error("No files were written to the output ZIP. Check your input.")

    # Clean up temporary files after processing
    if "temp_dir" in st.session_state and st.session_state["temp_dir"]:
        st.session_state["temp_dir"].cleanup()
        st.session_state.pop("temp_dir", None)


st.markdown("---")  # Adds a horizontal line as a separator
st.markdown(
    """
    Made by
    """
)
st.image("https://res.cloudinary.com/ace-cloud/image/fetch/f_auto,c_limit,w_256,q_auto/https://acecentre.org.uk/nav-logo.png", width=150)