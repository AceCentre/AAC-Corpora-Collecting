import streamlit as st
from lxml import etree as ET
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

def create_cdata(text):
    return ET.CDATA(text)

def extract_text_and_metadata_from_parameter(param_elem):
    """Extract full text and keep track of word metadata"""
    full_text = []
    metadata = []
    
    p_elem = param_elem.find('p')
    if p_elem is not None:
        for s_elem in p_elem.findall('s'):
            r_elem = s_elem.find('r')
            if r_elem is not None:
                word = r_elem.text or ''
                if word.strip():  # If it's an actual word
                    full_text.append(word)
                    # Store any attributes from the s element
                    meta = dict(s_elem.attrib)
                    metadata.append(('word', meta))
                else:  # It's a space
                    full_text.append(' ')
                    metadata.append(('space', {}))
    
    return ' '.join(full_text), metadata

def rebuild_parameter_with_metadata(param_elem, translated_text, original_metadata):
    """Rebuild the parameter structure with translated text and preserve metadata"""
    # Clear existing content while preserving the Parameter attributes
    attribs = dict(param_elem.attrib)
    param_elem.clear()
    for k, v in attribs.items():
        param_elem.set(k, v)
    
    # Create the basic structure
    p_elem = ET.SubElement(param_elem, 'p')
    
    # Split the translated text into words
    words = translated_text.strip().split()
    
    meta_idx = 0
    for i, word in enumerate(words):
        # Create word element
        s_elem = ET.SubElement(p_elem, 's')
        
        # Apply metadata if available
        if meta_idx < len(original_metadata):
            meta_type, meta_data = original_metadata[meta_idx]
            if meta_type == 'word':
                for k, v in meta_data.items():
                    s_elem.set(k, v)
        
        # Add the word
        r_elem = ET.SubElement(s_elem, 'r')
        r_elem.text = word
        meta_idx += 1
        
        # Add space after word (except last word)
        if i < len(words) - 1:
            s_space = ET.SubElement(p_elem, 's')
            r_space = ET.SubElement(s_space, 'r')
            r_space.text = create_cdata(' ')
            meta_idx += 1

def process_and_translate_xml(
    file, 
    tool, 
    source_lang, 
    target_lang, 
    api_key=None, 
    region=None, 
    tweak_xml=False, 
    debug_messages=None, 
    debug_log=None, 
    rate_limit_enabled=True
):
    if debug_messages is None:
        debug_messages = []

    def add_message(message):
        debug_messages.append(message)
        if debug_log:
            debug_log.text_area("Debug Log", "\n".join(debug_messages), height=300)

    try:
        parser = ET.XMLParser(remove_blank_text=True)
        tree = ET.parse(file, parser)
        root = tree.getroot()

        # Collect translatable texts
        translatable_texts = []
        elements_to_translate = []
        metadata_store = {}

        add_message("Parsing XML and collecting translatable texts...")
        for element in root.iter():
            # Skip known non-translatable elements
            if element.tag in ["Style", "Image", "ContentType", "ContentSubType"]:
                continue

            # Handle Parameter elements specially
            if element.tag == "Parameter":
                key = element.get("Key")
                if key == "text":
                    # Skip grid names in Jump.To commands
                    parent = element.getparent()
                    if parent is not None:
                        command_id = parent.get("ID")
                        if command_id == "Jump.To":
                            continue
                        
                    # For complex text parameters with <p><s><r> structure
                    if element.find('.//p') is not None:
                        full_text, metadata = extract_text_and_metadata_from_parameter(element)
                        if full_text.strip():
                            translatable_texts.append(full_text)
                            elements_to_translate.append(("parameter", element))
                            metadata_store[full_text] = metadata
                            add_message(f"Added complex parameter text for translation: {full_text}")
                    else:
                        # For simple text parameters (like in Speech.SpeakNow)
                        if element.text and element.text.strip():
                            translatable_texts.append(element.text)
                            elements_to_translate.append(("simple", element))
                            add_message(f"Added simple parameter text for translation: {element.text}")
            
            # Handle Caption elements
            elif element.tag == "Caption":
                if element.text and element.text.strip():
                    text = element.text.strip()
                    translatable_texts.append(text)
                    elements_to_translate.append(("caption", element))
                    add_message(f"Added caption for translation: {text}")

        # Perform batch translation with caching
        add_message("Translating collected texts...")
        translated_texts = []
        for text in translatable_texts:
            if text in st.session_state["translation_cache"]:
                translated_texts.append(st.session_state["translation_cache"][text])
                add_message(f"Cache hit: '{text}' -> '{st.session_state['translation_cache'][text]}'")
            else:
                translated_texts.append(None)

        # Translate only uncached texts
        texts_to_translate = [text for text, translated in zip(translatable_texts, translated_texts) if translated is None]
        if texts_to_translate:
            new_translations = translate_text(texts_to_translate, tool, source_lang, target_lang, api_key, region, rate_limit_enabled)
            for text, translation in zip(texts_to_translate, new_translations):
                st.session_state["translation_cache"][text] = translation
                translated_texts[translatable_texts.index(text)] = translation
                add_message(f"Translated: '{text}' -> '{translation}'")

        # Update XML with translated text
        add_message("Updating XML with translated texts...")
        for (elem_type, element), translated, original in zip(elements_to_translate, translated_texts, translatable_texts):
            if elem_type == "parameter":
                # Get the original metadata for this text if any
                original_metadata = metadata_store.get(original, [])
                rebuild_parameter_with_metadata(element, translated, original_metadata)
                add_message(f"Updated complex parameter text with: {translated}")
            elif elem_type == "caption":
                element.text = create_cdata(translated.strip() + ' ')
                add_message(f"Updated caption with CDATA: {translated}")
            else:  # simple
                element.text = translated
                add_message(f"Updated element text: {translated}")

        # Save modified XML
        translated_xml = BytesIO()
        tree.write(translated_xml, encoding="utf-8", xml_declaration=True, pretty_print=True)
        translated_xml.seek(0)
        add_message("Modified XML saved successfully.")
        return translated_xml
    except Exception as e:
        error_message = f"Error processing XML: {e}"
        add_message(error_message)
        st.error(error_message)
        return None

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
    [Grid 3 software](http://thinksmartbox.com/grid3). This will run a lot faster if you use a paid for translation tool - You'll just need to enter your key below if you use that.
    
    **Note: Please dont rely on this! This may be useful to get you started and will definitely be useful for phrases but for core word vocabulary systems be very wary of it!** 

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
        api_key = st.text_input("Enter your DeepL Translator API Key", type="password")
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

def add_message_to_debug_area(message, debug_messages, debug_log):
    """
    Adds a message to the debug log and updates the Streamlit text area dynamically.

    Args:
        message (str): The message to add to the debug log.
        debug_messages (list): List of existing debug messages.
        debug_log: Streamlit element placeholder for the debug text area.
    """
    debug_messages.append(message)
    if debug_log:  # Ensure debug_log is initialized
        debug_log.text_area("Debug Log", "\n".join(debug_messages), height=300)

# Main logic
debug_messages = []

# File upload
uploaded_file = st.file_uploader("Upload a Gridset file (.gridset)", type=["gridset"])
tweak_xml = st.checkbox("Tweak final Gridset for Better Language support (only use if it failed first time!)", value=False)
debug_log = st.empty() if st.checkbox("Enable Debug Output", value=False) else None


if uploaded_file:
    # Manage temporary directory and cache
    if "last_uploaded_file" not in st.session_state or st.session_state["last_uploaded_file"] != uploaded_file.name:
        # Remove previous temp directory if a new file is uploaded
        if "temp_dir" in st.session_state and st.session_state["temp_dir"]:
            st.session_state["temp_dir"].cleanup()
            st.session_state.pop("temp_dir", None)
        # Create a new temp directory and reset cache
        st.session_state["temp_dir"] = tempfile.TemporaryDirectory()
        st.session_state["translation_cache"] = {}
        st.session_state["last_uploaded_file"] = uploaded_file.name

    # Safely access the temp directory
    temp_dir = st.session_state["temp_dir"].name if "temp_dir" in st.session_state else None

    if temp_dir is None:
        st.error("Temporary directory is not available. Please re-upload the file.")
        st.stop()

    try:
        # Extract the uploaded file into the temp directory
        with zipfile.ZipFile(uploaded_file, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
        st.write("Files successfully extracted.")

        # Count total XML files for progress bar
        total_files = sum(
            1 for root, _, files in os.walk(temp_dir)
            for f in files 
            if f.endswith(".xml") and "Grids/" in os.path.relpath(root, temp_dir)
        )

        if total_files == 0:
            st.error("No XML files found in the uploaded gridset.")
            st.stop()

        # Initialize progress variables
        processed_files = set()  # Keep track of processed files
        current_progress = 0
        progress_bar = st.progress(0)
        progress_text = st.empty()  # Placeholder for progress text
        start_time = time.time()

        # Create ZIP file for translated content
        output_zip = BytesIO()
        with zipfile.ZipFile(output_zip, "w") as output_zip_ref:
            for root, _, files in os.walk(temp_dir):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    relative_path = os.path.relpath(file_path, temp_dir)

                    # Process only XML files in the "Grids/" directory
                    if (relative_path.startswith("Grids/") 
                        and file_name.endswith(".xml")
                        and file_path not in processed_files):
                        
                        processed_files.add(file_path)
                        try:
                            add_message_to_debug_area(f"Translating file: {file_name}", debug_messages, debug_log)

                            translated_xml = process_and_translate_xml(
                                file_path,
                                translation_tool,
                                source_lang,
                                target_lang,
                                api_key,
                                region,
                                tweak_xml=tweak_xml,
                                debug_messages=debug_messages,
                                debug_log=debug_log,
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

                    # Update progress bar only for XML files we're meant to process
                    if relative_path.startswith("Grids/") and file_name.endswith(".xml"):
                        current_progress = len(processed_files)
                        progress_percentage = int((current_progress / total_files) * 100)
                        progress_bar.progress(min(progress_percentage, 100))

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

            # Re-download button
            if st.button("Re-download"):
                st.download_button(
                    label="Download Translated Gridset",
                    data=output_zip,
                    file_name=translated_filename,
                    mime="application/zip",
                )

            # Start again button
            if st.button("Start Again"):
                st.session_state.clear()
                st.experimental_rerun()
    except Exception as e:
        st.error(f"An error occurred during processing: {e}")

    # Clean up temporary files after processing
    if "temp_dir" in st.session_state and st.session_state["temp_dir"]:
        st.session_state["temp_dir"].cleanup()
        st.session_state.pop("temp_dir", None)

st.markdown("---")  # Adds a horizontal line as a separator
st.markdown(
    """
    #### Related Tools
    - [AAC Keyboard Maker](https://aackeyboardmaker.streamlit.app/): Create custom keyboards for Grid 3 in various languages.
    - [TTS Voices Available](https://ttsvoicesavailable.streamlit.app/): Check if Text-to-Speech (TTS) is supported in your desired language.
    - [AAC Speak Helper](https://docs.acecentre.org.uk/products/aac-speak-helper-tool): A tool to work with Windows AAC Softwre to provide additional languages for TTS and translation


    Made by
    """
)
st.image("https://res.cloudinary.com/ace-cloud/image/fetch/f_auto,c_limit,w_256,q_auto/https://acecentre.org.uk/nav-logo.png", width=150)