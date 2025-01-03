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

MAX_CACHE_SIZE = 1000

translation_cache = {}

if "translation_cache" not in st.session_state:
    st.session_state["translation_cache"] = {}

def manage_cache():
    """Keep cache size under control"""
    if len(st.session_state["translation_cache"]) > MAX_CACHE_SIZE:
        # Remove oldest entries to keep size in check
        items = list(st.session_state["translation_cache"].items())
        st.session_state["translation_cache"] = dict(items[-MAX_CACHE_SIZE:])

def create_cdata(text):
    return ET.CDATA(text)

def extract_text_and_metadata_from_element(elem):
    """Extract full text and keep track of word metadata from either Parameter or WordList Text elements"""
    if elem is None:
        return '', []
        
    full_text = []
    metadata = []
    
    try:
        # Handle both direct <s> elements and those within <p>
        s_elements = elem.findall('.//s') or []
        for s_elem in s_elements:
            if s_elem is None:
                continue
                
            # Store the image attribute if present
            meta = dict(s_elem.attrib) if s_elem.attrib else {}
            
            # Process each <r> element within the <s>
            r_elements = s_elem.findall('r') or []
            for r_elem in r_elements:
                if r_elem is None:
                    continue
                    
                word = r_elem.text if r_elem is not None and r_elem.text is not None else ''
                if word and word.strip():  # If it's an actual word
                    full_text.append(word.strip())
                    metadata.append(('word', meta))
                elif word:  # It's a space or other whitespace
                    full_text.append(' ')
                    metadata.append(('space', {}))
    except Exception as e:
        st.error(f"Error extracting text: {e}")
        return '', []
    
    result = ' '.join(full_text)
    return result.strip(), metadata

def rebuild_element_with_metadata(elem, translated_text, original_metadata):
    """Rebuild either Parameter or WordList Text element structure with translated text and preserve metadata"""
    if elem is None:
        return
        
    if translated_text is None:
        translated_text = ''
    
    try:
        # Clear existing content while preserving attributes
        attribs = dict(elem.attrib) if elem.attrib else {}
        elem.clear()
        for k, v in attribs.items():
            if k is not None and v is not None:
                elem.set(k, v)
        
        # Handle empty or whitespace-only translations
        if not translated_text or not translated_text.strip():
            # Create minimal valid structure
            if len(elem.findall('.//p')) > 0:
                p_elem = ET.SubElement(elem, 'p')
                s_elem = ET.SubElement(p_elem, 's')
            else:
                s_elem = ET.SubElement(elem, 's')
            r_elem = ET.SubElement(s_elem, 'r')
            r_elem.text = ' '
            return
        
        # Split the translated text into words, handling None or empty cases
        words = [w for w in translated_text.strip().split() if w]
        if not words:
            words = [' ']
        
        # Check if we need a <p> wrapper (if original had one)
        needs_p = len(elem.findall('.//p')) > 0
        parent_elem = ET.SubElement(elem, 'p') if needs_p else elem
        
        meta_idx = 0
        current_s = None
        
        for i, word in enumerate(words):
            if word is None or not word.strip():
                continue
                
            # Get metadata for this word
            meta_data = {}
            if meta_idx < len(original_metadata):
                meta_type, meta_data = original_metadata[meta_idx]
                
                # Create new <s> element only if we need one (new word or different image)
                if current_s is None or meta_type == 'word':
                    current_s = ET.SubElement(parent_elem, 's')
                    # Apply metadata (like Image attribute)
                    for k, v in meta_data.items():
                        if k is not None and v is not None:
                            current_s.set(k, v)
            
            # Add the word
            r_elem = ET.SubElement(current_s, 'r')
            r_elem.text = word
            meta_idx += 1
            
            # Add space after word (except last word)
            if i < len(words) - 1:
                r_space = ET.SubElement(current_s, 'r')
                r_space.text = create_cdata(' ')
                meta_idx += 1
    except Exception as e:
        st.error(f"Error rebuilding element: {e}")

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

    def log_element_context(element):
        """Log context about the XML element being processed"""
        try:
            context = []
            # Get element path
            path = element.getroottree().getpath(element)
            context.append(f"XML Path: {path}")
            
            # Get element attributes
            if element.attrib:
                context.append("Attributes:")
                for k, v in element.attrib.items():
                    context.append(f"  {k}: {v}")
            
            # Get parent info
            parent = element.getparent()
            if parent is not None:
                context.append(f"Parent: {parent.tag}")
                if parent.attrib:
                    context.append("Parent Attributes:")
                    for k, v in parent.attrib.items():
                        context.append(f"  {k}: {v}")
            
            # Get text content preview
            if element.text:
                preview = element.text[:100] + "..." if len(element.text) > 100 else element.text
                context.append(f"Text Content: {preview}")
            
            return "\n".join(context)
        except Exception as e:
            return f"Error getting element context: {e}"

    try:
        parser = ET.XMLParser(remove_blank_text=True)
        tree = ET.parse(file, parser)
        root = tree.getroot()

        # Collect translatable texts
        translatable_texts = []
        elements_to_translate = []
        metadata_store = {}

        add_message("Parsing XML and collecting translatable texts...")
        current_element = None  # Keep track of current element being processed
        
        for element in root.iter():
            try:
                current_element = element
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
                        if element.find('.//p') is not None or element.find('.//s') is not None:
                            full_text, metadata = extract_text_and_metadata_from_element(element)
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
                
                # Handle WordList Text elements
                elif element.tag == "Text" and element.getparent() is not None and element.getparent().tag == "WordListItem":
                    if element.find('.//r') is not None:
                        full_text, metadata = extract_text_and_metadata_from_element(element)
                        if full_text.strip():
                            translatable_texts.append(full_text)
                            elements_to_translate.append(("wordlist", element))
                            metadata_store[full_text] = metadata
                            add_message(f"Added wordlist text for translation: {full_text}")
                
                # Handle Caption elements
                elif element.tag == "Caption":
                    if element.text and element.text.strip():
                        text = element.text.strip()
                        translatable_texts.append(text)
                        elements_to_translate.append(("caption", element))
                        add_message(f"Added caption for translation: {text}")
            except Exception as e:
                error_context = log_element_context(current_element)
                error_message = f"Error processing element:\n{error_context}\nError: {str(e)}"
                add_message(error_message)
                st.error(error_message)
                continue  # Continue with next element instead of failing completely

        # Perform batch translation with caching
        add_message("Translating collected texts...")
        translated_texts = []
        texts_to_translate = []
        cache_indices = []  # Keep track of which indices were from cache

        # First pass: check cache
        for i, text in enumerate(translatable_texts):
            if text in st.session_state["translation_cache"]:
                translated_texts.append(st.session_state["translation_cache"][text])
                add_message(f"Cache hit: '{text}' -> '{st.session_state['translation_cache'][text]}'")
                cache_indices.append(i)
            else:
                translated_texts.append(None)
                texts_to_translate.append(text)

        # Translate uncached texts
        if texts_to_translate:
            new_translations = translate_text(texts_to_translate, tool, source_lang, target_lang, api_key, region, rate_limit_enabled)
            
            # Update cache and translated_texts
            translation_idx = 0
            for i, translation in enumerate(translated_texts):
                if i not in cache_indices:
                    translated_texts[i] = new_translations[translation_idx]
                    st.session_state["translation_cache"][translatable_texts[i]] = new_translations[translation_idx]
                    add_message(f"Translated: '{translatable_texts[i]}' -> '{new_translations[translation_idx]}'")
                    translation_idx += 1

            # Manage cache size
            manage_cache()

        # Update XML with translated text
        add_message("Updating XML with translated texts...")
        current_element = None
        for (elem_type, element), translated, original in zip(elements_to_translate, translated_texts, translatable_texts):
            try:
                current_element = element
                if elem_type in ["parameter", "wordlist"]:
                    # Get the original metadata for this text if any
                    original_metadata = metadata_store.get(original, [])
                    rebuild_element_with_metadata(element, translated, original_metadata)
                    add_message(f"Updated {elem_type} text with: {translated}")
                elif elem_type == "caption":
                    # Handle None or empty translations for captions
                    if translated is None or not translated.strip():
                        translated = original or ''  # Fallback to original text or empty string
                    element.text = create_cdata(translated.strip() + ' ')
                    add_message(f"Updated caption with CDATA: {translated}")
                else:  # simple
                    # Handle None or empty translations for simple text
                    if translated is None or not translated.strip():
                        translated = original or ''  # Fallback to original text or empty string
                    element.text = translated
                    add_message(f"Updated element text: {translated}")
            except Exception as e:
                error_context = log_element_context(current_element)
                error_message = f"Error updating element:\n{error_context}\nError: {str(e)}"
                add_message(error_message)
                st.error(error_message)
                continue

        # Save modified XML
        translated_xml = BytesIO()
        tree.write(translated_xml, encoding="utf-8", xml_declaration=True, pretty_print=True)
        translated_xml.seek(0)
        add_message("Modified XML saved successfully.")
        return translated_xml
    except Exception as e:
        error_context = ""
        if 'current_element' in locals() and current_element is not None:
            error_context = log_element_context(current_element)
        error_message = f"Error processing XML:\n{error_context}\nError: {str(e)}"
        add_message(error_message)
        st.error(error_message)
        return None

def translate_text(text_list, tool, source_lang, target_lang, api_key=None, region=None, rate_limit_enabled=False):
    try:
        if not text_list:  # Handle empty list case
            return []

        # Deduplicate texts before translation to reduce API calls
        unique_texts = list(set(text for text in text_list if text))  # Filter out None/empty values
        if not unique_texts:  # If no valid texts after filtering
            return text_list
            
        text_map = {text: i for i, text in enumerate(text_list)}
        
        if tool == "Google":
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            if rate_limit_enabled:
                batch_size = 10
                translated_texts = [''] * len(unique_texts)
                
                for i in range(0, len(unique_texts), batch_size):
                    batch = unique_texts[i:i + batch_size]
                    try:
                        translations = translator.translate_batch(batch)
                        # Ensure translations list matches batch size
                        if translations and len(translations) == len(batch):
                            for j, trans in enumerate(translations):
                                translated_texts[i + j] = trans if trans else batch[j]
                        else:
                            # If translation failed, use original texts
                            for j, original in enumerate(batch):
                                translated_texts[i + j] = original
                    except Exception as batch_error:
                        st.error(f"Batch translation error: {batch_error}")
                        # Use original texts for failed batch
                        for j, original in enumerate(batch):
                            translated_texts[i + j] = original
                    
                    if i + batch_size < len(unique_texts):
                        time.sleep(0.5)
                
                # Create translation map with safety checks
                translation_map = {}
                for orig, trans in zip(unique_texts, translated_texts):
                    translation_map[orig] = trans if trans else orig
                
                # Map back to original order with fallback
                return [translation_map.get(text, text) for text in text_list]
            else:
                try:
                    translations = translator.translate_batch(unique_texts)
                    if translations and len(translations) == len(unique_texts):
                        translation_map = dict(zip(unique_texts, translations))
                    else:
                        translation_map = dict(zip(unique_texts, unique_texts))
                    return [translation_map.get(text, text) for text in text_list]
                except Exception as e:
                    st.error(f"Bulk translation error: {e}")
                    return text_list
                    
        elif tool == "Microsoft":
            if api_key and region:
                try:
                    translator = MicrosoftTranslator(api_key=api_key, source=source_lang, target=target_lang, region=region)
                    translations = translator.translate_batch(unique_texts)
                    if translations and len(translations) == len(unique_texts):
                        translation_map = dict(zip(unique_texts, translations))
                    else:
                        translation_map = dict(zip(unique_texts, unique_texts))
                    return [translation_map.get(text, text) for text in text_list]
                except Exception as e:
                    st.error(f"Microsoft translation error: {e}")
                    return text_list
            else:
                raise ValueError("Microsoft Translator requires both api_key and region.")
                
        elif tool == "DeepL":
            if api_key:
                try:
                    translator = DeeplTranslator(api_key=api_key, source=source_lang, target=target_lang)
                    translations = translator.translate_batch(unique_texts)
                    if translations and len(translations) == len(unique_texts):
                        translation_map = dict(zip(unique_texts, translations))
                    else:
                        translation_map = dict(zip(unique_texts, unique_texts))
                    return [translation_map.get(text, text) for text in text_list]
                except Exception as e:
                    st.error(f"DeepL translation error: {e}")
                    return text_list
            else:
                raise ValueError("DeepL requires an api_key.")
    except Exception as e:
        st.error(f"Translation error: {e}")
        return text_list  # Return original texts if translation fails

# Function to get supported languages
def get_supported_languages(tool, api_key=None, region=None):
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

# Streamlit app
st.title("Gridset Translator")
st.markdown(
    """
    This tool helps you translate [Grid3](https://thinksmartbox.com/grid3) gridsets from one language to another.
    Upload a gridset file (.gridset), select your translation options, and click Start Translation.
    """
)

# Initialize session state variables if they don't exist
if 'translation_started' not in st.session_state:
    st.session_state.translation_started = False
if 'translation_complete' not in st.session_state:
    st.session_state.translation_complete = False
if 'output_zip' not in st.session_state:
    st.session_state.output_zip = None
if 'translated_filename' not in st.session_state:
    st.session_state.translated_filename = None
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

# Start Again button at the top
if st.session_state.translation_started:
    if st.button("Start New Translation"):
        st.session_state.clear()
        st.rerun()

# Only show options if translation hasn't started
if not st.session_state.translation_started:
    uploaded_file = st.file_uploader(
        "Choose a gridset file",
        type=["gridset"],
        help="Upload a Grid3 gridset file (.gridset)",
    )

    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        st.write("File uploaded successfully!")

        # Translation options
        translation_tool = st.selectbox(
            "Select Translation Tool",
            ["Google", "Microsoft", "DeepL"],
            help="Choose the translation service to use",
        )

        # API configuration first
        api_key = None
        region = None
        valid_credentials = True
        
        if translation_tool in ["Microsoft", "DeepL"]:
            api_key = st.text_input(
                f"{translation_tool} API Key",
                type="password",
                help=f"Enter your {translation_tool} API key",
            )
            if translation_tool == "Microsoft":
                region = st.text_input(
                    "Azure Region",
                    help="Enter your Azure region (e.g., westeurope)",
                )
            
            # Check if credentials are provided
            if not api_key:
                st.warning(f"Please enter your {translation_tool} API key to see available languages.")
                valid_credentials = False
            elif translation_tool == "Microsoft" and not region:
                st.warning("Please enter your Azure region to see available languages.")
                valid_credentials = False

        # Only show language selection if we have valid credentials
        if valid_credentials:
            try:
                # Get languages and ensure English is first
                languages = get_supported_languages(translation_tool, api_key, region)
                if not languages:
                    st.error("Failed to retrieve supported languages. Please check your API credentials.")
                    valid_credentials = False
                else:
                    if "english" in languages:
                        languages.remove("english")
                        languages.insert(0, "english")
                    elif "en" in languages:
                        languages.remove("en")
                        languages.insert(0, "en")

                    col1, col2 = st.columns(2)
                    with col1:
                        source_lang = st.selectbox(
                            "Source Language",
                            languages,
                            index=0  # English will always be first now
                        )
                    with col2:
                        target_lang = st.selectbox(
                            "Target Language",
                            languages,
                            index=1 if len(languages) > 1 else 0
                        )

                    # Advanced options in expander
                    with st.expander("Advanced Options"):
                        tweak_xml = st.checkbox(
                            "Use CDATA for text elements",
                            value=False,
                            help="Experimental: This maybe useful to fix issues in some languages where the text breaks the grid eg Urdu."
                        )
                        rate_limit = st.checkbox(
                            "Enable rate limiting",
                            value=True,
                            help="Slow down translation requests to avoid API limits",
                        )
                        show_debug = st.checkbox(
                            "Show debug output",
                            value=False,
                            help="Show detailed progress and debug information in a scrolling box"
                        )

                    # Start Translation button
                    if st.button("Start Translation"):
                        st.session_state.translation_started = True
                        st.session_state.show_debug = show_debug
                        st.session_state.translation_tool = translation_tool
                        st.session_state.source_lang = source_lang
                        st.session_state.target_lang = target_lang
                        st.session_state.api_key = api_key
                        st.session_state.region = region
                        st.session_state.tweak_xml = tweak_xml
                        st.session_state.rate_limit = rate_limit
                        st.rerun()
            except Exception as e:
                st.error(f"Error retrieving languages: {str(e)}")
                st.error("Please check your API credentials and try again.")

# Process translation if started
if st.session_state.translation_started and not st.session_state.translation_complete:
    # Create debug log area
    debug_log = st.empty() if st.session_state.get('show_debug', False) else None
    debug_messages = []

    # Get translation settings from session state
    translation_tool = st.session_state.translation_tool
    source_lang = st.session_state.source_lang
    target_lang = st.session_state.target_lang
    api_key = st.session_state.api_key
    region = st.session_state.region
    tweak_xml = st.session_state.tweak_xml
    rate_limit = st.session_state.rate_limit

    # Manage temporary directory and cache
    if "last_uploaded_file" not in st.session_state or st.session_state["last_uploaded_file"] != st.session_state.uploaded_file.name:
        if "temp_dir" in st.session_state and st.session_state["temp_dir"]:
            st.session_state["temp_dir"].cleanup()
        st.session_state["temp_dir"] = tempfile.TemporaryDirectory()
        st.session_state["last_uploaded_file"] = st.session_state.uploaded_file.name

    # Safely access the temp directory
    temp_dir = st.session_state["temp_dir"].name if "temp_dir" in st.session_state else None

    if temp_dir is None:
        st.error("Temporary directory is not available. Please re-upload the file.")
        st.stop()

    try:
        # Extract the uploaded file into the temp directory
        with st.spinner('Extracting files from gridset...'):
            with zipfile.ZipFile(st.session_state.uploaded_file, "r") as zip_ref:
                zip_ref.extractall(temp_dir)
            st.success("Files successfully extracted!")

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
        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zip_out:
            with st.spinner('Translating gridset contents...'):
                for root, dirs, files in os.walk(temp_dir):
                    for file_name in files:
                        file_path = os.path.join(root, file_name)
                        relative_path = os.path.relpath(file_path, temp_dir)

                        # Process only XML files in the "Grids/" directory
                        if (relative_path.startswith("Grids/") 
                            and file_name.endswith(".xml")
                            and file_path not in processed_files):
                            
                            processed_files.add(file_path)
                            try:
                                debug_messages.append(f"Translating file: {file_name}")

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
                                    zip_out.writestr(relative_path, translated_xml.read())
                                else:
                                    st.error(f"Failed to translate: {file_name}")
                            except Exception as e:
                                st.error(f"Error translating file {file_name}: {e}")
                        else:
                            # Copy non-XML files directly
                            with open(file_path, "rb") as f:
                                zip_out.writestr(relative_path, f.read())

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
            translated_filename = f"{os.path.splitext(st.session_state.uploaded_file.name)[0]}-{target_lang}.gridset"

            # Store the output zip and filename in session state
            st.session_state.output_zip = output_zip
            st.session_state.translated_filename = translated_filename
            st.session_state.translation_complete = True

            # Show download button
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

# Show download button if translation is complete
elif st.session_state.translation_complete and st.session_state.output_zip is not None:
    st.success("Translation complete! You can download your translated gridset below.")
    st.download_button(
        label="Download Translated Gridset",
        data=st.session_state.output_zip,
        file_name=st.session_state.translated_filename,
        mime="application/zip",
    )

st.markdown("---")  # Adds a horizontal line as a separator
st.markdown(
    """
    #### Please Note
    This is not meant to replace the role of a translator, but it can be useful to "bulk" translate large sets of words and phrases to get you started. Be very careful of using this on core word systems in particular. Languages don't all translate the same way.

    #### Privacy
    This tool does not collect or store any of your data. It does not modify the original gridset in any way oher than translates strings it can find. It does not store locally or anywhere the data from the gridset. We don't track usage etc. **BUT BE AWARE OF THIS!**  If you use Google as a translation engine you are in effect passing all data from the gridset to Google Translate. Just like if you copy and pasted each cell. Tip: Remove any Personalised Data from your gridset first before uploading it (it wont translate anyway!) or use Microsoft and use your own key

    #### Related Tools
    - [AAC Keyboard Maker](https://aackeyboardmaker.streamlit.app/): Create custom keyboards for Grid 3 in various languages.
    - [TTS Voices Available](https://ttsvoicesavailable.streamlit.app/): Check if Text-to-Speech (TTS) is supported in your desired language.
    - [AAC Speak Helper](https://docs.acecentre.org.uk/products/aac-speak-helper-tool): A tool to work with Windows AAC Software to provide additional languages for TTS and translation


    Made by
    """
)
st.image("https://res.cloudinary.com/ace-cloud/image/fetch/f_auto,c_limit,w_256,q_auto/https://acecentre.org.uk/nav-logo.png", width=150)