import os 

from dotenv import load_dotenv
from groq import Groq
import pandas as pd 
import time
import streamlit as st
from datetime import datetime
import numpy as np
import tempfile
import io
import traceback
import logging
import gc
import warnings
import base64
import hashlib
import json
import os
from datetime import datetime, timedelta
import streamlit.components.v1 as components
import gc
import fitz
from openai import OpenAI


warnings.filterwarnings('ignore', category=RuntimeWarning)
logging.getLogger('streamlit.watcher.local_sources_watcher').setLevel(logging.ERROR)

st.set_page_config(
    page_title="AlKhayyat Investment ASN Project",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"Current PATH: {os.environ.get('PATH')}")
logger.info(f"Current working directory: {os.getcwd()}")

load_dotenv()
# groq_api_key = os.getenv("GROQ_API_KEY")
# groq_client = Groq(api_key=groq_api_key)
# print(os.environ['PATH'])
# 
open_api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=open_api_key)

def admin_tracking_tab():
    """Display user tracking data for admin"""
    try:
        if os.path.exists(USER_TRACKING_FILE):
            df = pd.read_excel(USER_TRACKING_FILE)
            
            st.markdown("### 📊 User Upload Tracking")
            
            search_term = st.text_input("🔍 Search Users or Details:", key="admin_search")
            
            if search_term:
                mask = df.astype(str).apply(
                    lambda x: x.str.contains(search_term, case=False)
                ).any(axis=1)
                filtered_df = df[mask]
            else:
                filtered_df = df

            st.dataframe(
                filtered_df, 
                use_container_width=True,
                hide_index=True
            )

            st.markdown("### 📈 Upload Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Users", len(df['Username'].unique()))
            
            with col2:
                st.metric("Total Files Uploaded", df['Files Uploaded'].sum())
            
            with col3:
                st.metric("Total Rows Processed", df['Rows Processed'].sum())
            
            if st.download_button(
                "📥 Download Tracking File", 
                data=open(USER_TRACKING_FILE, 'rb').read(),
                file_name="user_tracking.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_tracking"
            ):
                st.success("Tracking file downloaded successfully!")
        
        else:
            st.warning("No user tracking data available.")
    
    except Exception as e:
        st.error(f"Error displaying tracking data: {str(e)}")


# def display_excel_native(excel_data):
#     """Display Excel data using native Streamlit components with persistent editing"""
#     try:
#         df = pd.read_excel(io.BytesIO(excel_data))

#         excel_file = io.BytesIO(excel_data)
#         xl = pd.ExcelFile(excel_file)
#         sheet_names = xl.sheet_names

#         if len(sheet_names) > 1:
#             selected_sheet = st.selectbox("Select Sheet:", sheet_names)
#             df = pd.read_excel(excel_file, sheet_name=selected_sheet)

#         session_key = f"edited_df_{datetime.now().strftime('%Y%m%d')}"
        
#         if session_key not in st.session_state:
#             st.session_state[session_key] = df.copy()
        
#         edited_df = st.data_editor(
#             st.session_state[session_key],
#             use_container_width=True,
#             num_rows="dynamic",
#             height=600,
#             key=f'grid_{datetime.now().strftime("%Y%m%d%H%M%S")}',
#             column_config={col: st.column_config.Column(
#                 width="auto",
#                 help=f"Column: {col}"
#             ) for col in df.columns}
#         )
        
#         st.session_state[session_key] = edited_df
        
#         search = st.text_input("🔍 Search in table:", key="search_input")
#         if search:
#             mask = edited_df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
#             filtered_df = edited_df[mask]
#         else:
#             filtered_df = edited_df
            
#         st.markdown(f"**Total Rows:** {len(filtered_df)} | **Total Columns:** {len(filtered_df.columns)}")
        
#         if st.button("💾 Save Changes", key="save_changes"):
#             try:
#                 st.session_state.saved_df = edited_df.copy()
                
#                 save_path = save_uploaded_files(
#                     st.session_state.username,
#                     st.session_state.uploaded_pdfs,
#                     st.session_state.saved_df
#                 )
                
#                 if save_path:
#                     st.success("✅ Changes saved successfully!")
                    
#                     col1, col2 = st.columns(2)
                    
#                     with col1:
#                         buffer = io.BytesIO()
#                         with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
#                             edited_df.to_excel(writer, index=False)
                        
#                         st.download_button(
#                             label="📥 Download Edited Excel",
#                             data=buffer.getvalue(),
#                             file_name="edited_data.xlsx",
#                             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#                             key="download_edited"
#                         )
                    
#                     with col2:
#                         buffer_original = io.BytesIO()
#                         with pd.ExcelWriter(buffer_original, engine='openpyxl') as writer:
#                             df.to_excel(writer, index=False)
                        
#                         st.download_button(
#                             label="📥 Download Original Excel",
#                             data=buffer_original.getvalue(),
#                             file_name="original_data.xlsx",
#                             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#                             key="download_original"
#                         )
            
#             except Exception as e:
#                 st.error(f"Error saving changes: {str(e)}")
        
#         return edited_df
        
#     except Exception as e:
#         st.error(f"Error displaying Excel file: {str(e)}")
#         return None



def display_excel_native(excel_data):
    """Display Excel data with proper handling of both bytes and DataFrame inputs"""
    try:
        if isinstance(excel_data, pd.DataFrame):
            df = excel_data
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            excel_bytes = buffer.getvalue()
        else:
            # Assume it's bytes
            excel_bytes = excel_data
            df = pd.read_excel(io.BytesIO(excel_bytes))

        try:
            excel_file = io.BytesIO(excel_bytes)
            xl = pd.ExcelFile(excel_file)
            sheet_names = xl.sheet_names

            if len(sheet_names) > 1:
                selected_sheet = st.selectbox("Select Sheet:", sheet_names)
                df = pd.read_excel(excel_file, sheet_name=selected_sheet)
        except Exception as sheet_error:
            pass

        session_key = f"edited_df_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        if session_key not in st.session_state:
            st.session_state[session_key] = df.copy()
        
        edited_df = st.data_editor(
            df,  
            use_container_width=True,
            num_rows="dynamic",
            height=600,
            key=f'grid_{datetime.now().strftime("%Y%m%d%H%M%S")}',  
            column_config={col: st.column_config.Column(
                width="auto",
                help=f"Column: {col}"
            ) for col in df.columns}
        )
        
        search_key = f"search_input_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        # commented to remove search
        # search = st.text_input("🔍 Search in table: 2", key=search_key)
        
        # if search:
        #     mask = edited_df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
        #     filtered_df = edited_df[mask]
        # else:
        #     filtered_df = edited_df
            
        # st.markdown(f"**Total Rows:** {len(filtered_df)} | **Total Columns:** {len(filtered_df.columns)}")
        #commented to remove search
        save_key = f"save_changes_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        save_key_updated = f"save_changes_updated"
        if st.button("💾 Save Changes", key=save_key_updated):
            try:
                st.session_state.saved_df = edited_df.copy()
                
                pdf_files = []
                if hasattr(st.session_state, 'uploaded_pdfs') and st.session_state.uploaded_pdfs:
                    pdf_files = st.session_state.uploaded_pdfs
                
                save_path = save_uploaded_files(
                    st.session_state.username,
                    pdf_files,
                    edited_df 
                )
                
                if save_path:
                    st.success("✅ Changes saved successfully!")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                      
                        buffer = io.BytesIO()
                        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                            edited_df.to_excel(writer, index=False)
                        
                        st.download_button(
                            label="📥 Download Edited Excel",
                            data=buffer.getvalue(),
                            file_name="edited_data.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"download_edited_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                        )
                    
                    with col2:
                        buffer_original = io.BytesIO()
                        with pd.ExcelWriter(buffer_original, engine='openpyxl') as writer:
                            df.to_excel(writer, index=False)
                        
                        st.download_button(
                            label="📥 Download Original Excel",
                            data=buffer_original.getvalue(),
                            file_name="original_data.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"download_original_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                        )
            
            except Exception as e:
                st.error(f"Error saving changes: {str(e)}")
        
        return edited_df
        
    except Exception as e:
        st.error(f"Error displaying Excel file: {str(e)}")
        return None

def cleanup_temp_files():
    """Clean up any leftover temporary files"""
    if 'cleanup_files' in st.session_state:
        for tmp_path in st.session_state.cleanup_files[:]:  
            try:
                if os.path.exists(tmp_path):
                    gc.collect()  
                    os.unlink(tmp_path)
                st.session_state.cleanup_files.remove(tmp_path)
            except Exception:
                pass  

# def process_uploaded_files(pdfs_to_process):
#     """Process uploaded PDF files with enhanced handling for large files"""
#     try:
#         if st.session_state.edited_df is not None:
            
#             edited_df = display_excel_native(pd.DataFrame(st.session_state.edited_df))
#             if edited_df is not None:
#                 st.session_state.edited_df = edited_df
#         else:
            
#             progress_bar = st.progress(0)
#             status_text = st.empty()
            
#             total_files = len(pdfs_to_process)
#             total_rows_processed = 0
#             all_data = []
#             all_headers = None
            
#             for idx, uploaded_pdf_file in enumerate(pdfs_to_process):
#                 try:
#                     status_text.text(f"Processing file {idx + 1} of {total_files}: {uploaded_pdf_file.name}")
                    
#                     with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
#                         tmp_file.write(uploaded_pdf_file.getvalue())
#                         tmp_path = tmp_file.name
                        
#                         with st.spinner(f"Extracting text from {uploaded_pdf_file.name}..."):
#                             pdf_text = extract_text_pdf(tmp_path)
                            
#                             if pdf_text:
#                                 with st.spinner("Processing extracted text..."):
#                                     estimated_tokens = len(pdf_text) // 3
#                                     if estimated_tokens > 6000:
#                                         st.info(f"Large document detected ({estimated_tokens} est. tokens). Processing in chunks...")
                                    
#                                     invoice_info = using_groq(pdf_text)
#                                     rows_in_file = count_processed_rows(invoice_info)
#                                     total_rows_processed += rows_in_file
                                    
#                                     headers, data_rows = process_invoice_lines(
#                                         invoice_info, 
#                                         ""
#                                     )
                                    
#                                     if headers and data_rows:
#                                         if all_headers is None:
#                                             all_headers = headers
                                        
#                                         all_data.extend(data_rows)
                        
#                         try:
#                             os.unlink(tmp_path)
#                         except Exception as e:
#                             st.warning(f"Could not remove temporary file: {str(e)}")
#                             if 'cleanup_files' not in st.session_state:
#                                 st.session_state.cleanup_files = []
#                             st.session_state.cleanup_files.append(tmp_path)
                        
#                 except Exception as e:
#                     st.error(f"Error processing {uploaded_pdf_file.name}: {str(e)}")
                
#                 progress_bar.progress((idx + 1) / total_files)
#                 gc.collect()
            
#             if all_data and all_headers:
#                 df = pd.DataFrame(all_data, columns=all_headers)
#                 st.session_state.edited_df = df.copy()
                
#                 edited_df = display_excel_native(df)
#                 if edited_df is not None:
#                     st.session_state.edited_df = edited_df
#             else:
#                 st.error("No valid data could be extracted from the invoices")
            
#             update_user_tracking(
#                 username=st.session_state.username,
#                 files_uploaded=total_files,
#                 rows_processed=total_rows_processed
#             )
    
#     except Exception as e:
#         st.error(f"Error processing files: {str(e)}")
#         st.error(traceback.format_exc())



def process_uploaded_files(pdfs_to_process):
    """Process uploaded PDF files with enhanced handling for large files and improved error recovery"""
    try:
        if st.session_state.edited_df is not None:
            if isinstance(st.session_state.edited_df, pd.DataFrame):
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    st.session_state.edited_df.to_excel(writer, index=False)
                excel_data = buffer.getvalue()
                
                edited_df = display_excel_native(excel_data)
                if edited_df is not None:
                    st.session_state.edited_df = edited_df
            else:
                edited_df = display_excel_native(st.session_state.edited_df)
                if edited_df is not None:
                    st.session_state.edited_df = edited_df
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_files = len(pdfs_to_process)
            total_rows_processed = 0
            all_data = []
            all_headers = None
            
            temp_files_to_clean = []
            
            for idx, uploaded_pdf_file in enumerate(pdfs_to_process):
                tmp_path = None
                try:
                    status_text.text(f"Processing file {idx + 1} of {total_files}: {uploaded_pdf_file.name}")
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f'_{idx}_{datetime.now().strftime("%Y%m%d%H%M%S%f")}.pdf') as tmp_file:
                        tmp_file.write(uploaded_pdf_file.getvalue())
                        tmp_path = tmp_file.name
                        temp_files_to_clean.append(tmp_path)
                        
                        with st.spinner(f"Extracting text from {uploaded_pdf_file.name}..."):
                            pdf_text = extract_text_pdf(tmp_path)
                            
                            if pdf_text:
                                with st.spinner("Processing extracted text using AKI-GPT..."):
                                    estimated_tokens = len(pdf_text) // 3
                                    if estimated_tokens > 6000:
                                        st.info(f"Large document detected ({estimated_tokens} est. tokens). Processing in chunks...")
                                    
                                    invoice_info = using_groq(pdf_text)
                                    rows_in_file = count_processed_rows(invoice_info)
                                    total_rows_processed += rows_in_file
                                    
                                    headers, data_rows = process_invoice_lines(
                                        invoice_info, 
                                        ""
                                    )
                                    
                                    if headers and data_rows:
                                        if all_headers is None:
                                            all_headers = headers
                                        
                                        all_data.extend(data_rows)
                
                except Exception as e:
                    st.error(f"Error processing {uploaded_pdf_file.name}: {str(e)}")
                
                progress_bar.progress((idx + 1) / total_files)
                gc.collect()
            
            cleanup_temp_files_safely(temp_files_to_clean)
            
            if all_data and all_headers:
                df = pd.DataFrame(all_data, columns=all_headers)
                
                st.session_state.edited_df = df.copy()
                
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                excel_data = buffer.getvalue()
                
                edited_df = display_excel_native(excel_data)
                if edited_df is not None:
                    st.session_state.edited_df = edited_df
            else:
                st.error("No valid data could be extracted from the invoices")
            
            update_user_tracking(
                username=st.session_state.username,
                files_uploaded=total_files,
                rows_processed=total_rows_processed
            )
    
    except Exception as e:
        st.error(f"Error processing files: {str(e)}")
        st.error(traceback.format_exc())



def cleanup_temp_files_safely(file_paths):
    """Safely clean up temporary files with enhanced error handling"""
    if not file_paths:
        return
    
    for tmp_path in file_paths:
        try:
            if os.path.exists(tmp_path):
                gc.collect()
                
                time.sleep(0.1)
                
                os.unlink(tmp_path)
                
        except Exception as e:
            print(f"Could not remove temporary file: {str(e)}")
            
            if 'cleanup_files' not in st.session_state:
                st.session_state.cleanup_files = []
            if tmp_path not in st.session_state.cleanup_files:
                st.session_state.cleanup_files.append(tmp_path)

def create_editable_grid(df, key_prefix=""):
    """
    Create an editable grid using Streamlit data editor
    """
    try:
        column_config = {
            col: st.column_config.Column(
                width="auto",
                help=f"Edit {col}"
            ) for col in df.columns
        }
        
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            column_config=column_config,
            key=f"{key_prefix}_grid_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            height=600
        )
        
        search_term = st.text_input(
            "🔍 Search in table:",
            key=f"{key_prefix}_search_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        
        if search_term:
            
            mask = edited_df.astype(str).apply(
                lambda x: x.str.contains(search_term, case=False)
            ).any(axis=1)
            filtered_df = edited_df[mask]
        else:
            filtered_df = edited_df
            
        st.markdown(f"**Total Rows:** {len(filtered_df)} | **Total Columns:** {len(filtered_df.columns)}")
        
        return edited_df, filtered_df
        
    except Exception as e:
        st.error(f"Error in create_editable_grid: {str(e)}")
        return df, df


def display_extracted_data(df):
    """Display and manage editable extracted data with persistent state"""
    try:
        st.markdown("### 📝 Extracted and Edited Data")
        
        if 'grid_key' not in st.session_state:
            st.session_state.grid_key = 'data_editor_1'
            
        if 'editor_data' not in st.session_state:
            st.session_state.editor_data = df.copy()
        
        search_query = st.text_input("🔍 Search in table 1:", key="search_input")
        
        display_data = st.session_state.editor_data.copy()
        if search_query:
            mask = display_data.astype(str).apply(
                lambda x: x.str.contains(search_query, case=False)
            ).any(axis=1)
            display_data = display_data[mask]
        
        edited_df = st.data_editor(
            display_data,
            use_container_width=True,
            num_rows="dynamic",
            key=st.session_state.grid_key,
            height=600,
            column_config={
                col: st.column_config.Column(
                    width="auto",
                    help=f"Edit {col}"
                ) for col in df.columns
            }
        )
        
        st.session_state.editor_data = edited_df
        
        st.markdown(f"**Total Rows:** {len(edited_df)} | **Total Columns:** {len(edited_df.columns)}")
        
        if st.button("💾 Save Changes", key="save_changes"):
            try:
                st.session_state.saved_df = edited_df.copy()
                st.session_state.edited_df = edited_df.copy()
                
                save_path = save_uploaded_files(
                    st.session_state.username,
                    st.session_state.uploaded_pdfs,
                    st.session_state.saved_df
                )
                
                if save_path:
                    st.success("✅ Changes saved successfully!")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        buffer = io.BytesIO()
                        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                            edited_df.to_excel(writer, index=False)
                        
                        st.download_button(
                            label="📥 Download Edited Excel",
                            data=buffer.getvalue(),
                            file_name="edited_data.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="download_edited"
                        )
                    
                    with col2:
                        buffer_original = io.BytesIO()
                        with pd.ExcelWriter(buffer_original, engine='openpyxl') as writer:
                            df.to_excel(writer, index=False)
                        
                        st.download_button(
                            label="📥 Download Original Excel",
                            data=buffer_original.getvalue(),
                            file_name="original_data.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="download_original"
                        )
            
            except Exception as e:
                st.error(f"Error saving changes: {str(e)}")
        
        return edited_df
        
    except Exception as e:
        st.error(f"Error displaying extracted data: {str(e)}")
        return df


def modify_history_tab():
    st.markdown("### 📂 Previous Uploads")
    user_uploads = get_user_uploads(st.session_state.username)
    
    if not user_uploads.empty:
        for idx, row in user_uploads.iterrows():
            session_id = f"session_{idx}"
            
            with st.expander(f"Upload from {row['Upload Date']}"):
                view_tab, download_tab, share_tab = st.tabs(["View Files", "Download Files", "Share Files"])
                
                with view_tab:
                    st.markdown("**📄 View Invoice PDFs:**")
                    for pdf_idx, pdf_name in enumerate(row['Invoice Files'].split(', ')):
                        pdf_path = os.path.join(row['Path'], pdf_name)
                        if os.path.exists(pdf_path):
                            if st.button(f"View {pdf_name}", key=f"view_pdf_{session_id}_{pdf_idx}"):
                                with open(pdf_path, 'rb') as pdf_file:
                                    pdf_data = pdf_file.read()
                                    display_pdf(pdf_data)
                    
                    st.markdown("**📊 View Excel Result:**")
                    excel_path = os.path.join(row['Path'], row['Excel Result'])
                    if os.path.exists(excel_path):
                        if st.button(f"View {row['Excel Result']}", key=f"view_excel_{session_id}"):
                            with open(excel_path, 'rb') as excel_file:
                                excel_data = excel_file.read()
                                display_excel_native(excel_data)
                
                with download_tab:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📄 Download Invoice PDFs:**")
                        for pdf_idx, pdf_name in enumerate(row['Invoice Files'].split(', ')):
                            pdf_path = os.path.join(row['Path'], pdf_name)
                            if os.path.exists(pdf_path):
                                st.download_button(
                                    f"📥 {pdf_name}",
                                    download_stored_file(pdf_path),
                                    file_name=pdf_name,
                                    mime="application/pdf",
                                    key=f"download_pdf_{session_id}_{pdf_idx}"
                                )
                    
                    with col2:
                        st.markdown("**📊 Download Excel Result:**")
                        excel_path = os.path.join(row['Path'], row['Excel Result'])
                        if os.path.exists(excel_path):
                            st.download_button(
                                f"📥 {row['Excel Result']}",
                                download_stored_file(excel_path),
                                file_name=row['Excel Result'],
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key=f"download_excel_{session_id}"
                            )
                
                with share_tab:
                    st.markdown("**🔗 Share Files:**")
                    if st.button("Generate Links", key=f"share_{session_id}"):
                        share_links = []
                        
                        for pdf_name in row['Invoice Files'].split(', '):
                            pdf_path = os.path.join(row['Path'], pdf_name)
                            if os.path.exists(pdf_path):
                                pdf_link = generate_share_link(pdf_path)
                                if pdf_link:
                                    share_links.append((pdf_name, pdf_link))
                        
                        excel_path = os.path.join(row['Path'], row['Excel Result'])
                        if os.path.exists(excel_path):
                            excel_link = generate_share_link(excel_path)
                            if excel_link:
                                share_links.append((row['Excel Result'], excel_link))
                        
                        if share_links:
                            st.markdown("**Generated Links:**")
                            for link_idx, (file_name, link) in enumerate(share_links):
                                with st.container():
                                    st.text(file_name)
                                    st.code(link)
                                    if st.button(
                                        "📋 Copy Link",
                                        key=f"copy_{session_id}_{link_idx}"
                                    ):
                                        st.write(f"```{link}```")
                                    st.markdown("---")
    else:
        st.info("No previous uploads found")

    """Display Excel data using native Streamlit components"""
    try:
        df = pd.read_excel(io.BytesIO(excel_data))
        
        excel_file = io.BytesIO(excel_data)
        xl = pd.ExcelFile(excel_file)
        sheet_names = xl.sheet_names
        
        if len(sheet_names) > 1:
            selected_sheet = st.selectbox("Select Sheet:", sheet_names)
            df = pd.read_excel(excel_file, sheet_name=selected_sheet)
            
        search = st.text_input("🔍 Search in table:", key="excel_search")
        if search:
            mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
            df = df[mask]
        
        st.dataframe(
            df,
            use_container_width=True,
            height=600,
            hide_index=True
        )
        
        st.download_button(
            "📥 Download Excel File",
            excel_data,
            file_name="downloaded_file.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        return df
    except Exception as e:
        st.error(f"Error displaying Excel file: {str(e)}")
        return None

def display_pdf(pdf_data):
    """Display PDF as images while maintaining PDF download capability"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
            tmp_pdf.write(pdf_data)
            pdf_path = tmp_pdf.name


        st.download_button(
            label="📥 Download PDF",
            data=pdf_data,
            file_name="document.pdf",
            mime="application/pdf"
        )

        os.unlink(pdf_path)
        
    except Exception as e:
        st.error(f"Error displaying PDF: {str(e)}")
        st.download_button(
            label="⚠️ Download PDF",
            data=pdf_data,
            file_name="document.pdf",
            mime="application/pdf"
        )

def generate_share_link(file_path, expiry_days=7):
    """Generate a shareable link for a file"""
    try:
        file_hash = hashlib.md5(file_path.encode()).hexdigest()
        expiry_date = (datetime.now() + timedelta(days=expiry_days)).strftime('%Y-%m-%d')
        
        share_info = {
            'file_path': file_path,
            'expiry_date': expiry_date,
            'original_filename': os.path.basename(file_path)
        }
        
        shares_dir = 'storage/shares'
        os.makedirs(shares_dir, exist_ok=True)
        
        share_file = os.path.join(shares_dir, f'{file_hash}.json')
        with open(share_file, 'w') as f:
            json.dump(share_info, f)
            
        base_url = "https://aki-asn.streamlit.app"
        
        share_link = f"{base_url}/?share={file_hash}"
        
        return share_link
        
    except Exception as e:
        st.error(f"Error generating share link: {str(e)}")
        return None

def auto_download_shared_file():
    """Automatically handle file download based on URL parameters"""
    try:
        current_path = st.query_params.get('path', '')
        
        if current_path.startswith('download/'):
            file_hash = current_path.split('/')[-1]
            share_file = f'storage/shares/{file_hash}.json'
            
            if not os.path.exists(share_file):
                st.error("This download link is invalid or has expired.")
                return
            
            with open(share_file, 'r') as f:
                share_info = json.load(f)
            
            expiry_date = datetime.strptime(share_info['expiry_date'], '%Y-%m-%d')
            if datetime.now() > expiry_date:
                os.remove(share_file)
                st.error("This download link has expired.")
                return
            
            file_path = share_info['file_path']
            if not os.path.exists(file_path):
                st.error("The file is no longer available.")
                return
            
            file_data = download_stored_file(file_path)
            if file_data:
                original_filename = share_info['original_filename']
                mime_type = ("application/pdf" if original_filename.lower().endswith('.pdf') 
                           else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                
                st.markdown("""
                    <style>
                        .stDownloadButton button {
                            width: 100%;
                            height: 60px;
                            font-size: 20px;
                            margin-top: 20px;
                        }
                        .centered {
                            text-align: center;
                            padding: 20px;
                        }
                    </style>
                """, unsafe_allow_html=True)
                
                st.markdown(f"<div class='centered'><h2>📥 Downloading {original_filename}</h2></div>", 
                          unsafe_allow_html=True)
                
                components.html(
                    f"""
                    <html>
                        <body>
                            <script>
                                window.onload = function() {{
                                    setTimeout(function() {{
                                        document.getElementById('download-button').click();
                                    }}, 500);
                                }}
                            </script>
                        </body>
                    </html>
                    """,
                    height=0,
                )
                
                st.download_button(
                    label=f"Download {original_filename}",
                    data=file_data,
                    file_name=original_filename,
                    mime=mime_type,
                    key="download-button"
                )
                
                st.markdown("<div class='centered'><p>If the download doesn't start automatically, click the button above.</p></div>", 
                          unsafe_allow_html=True)
                
            else:
                st.error("Unable to prepare the file for download.")
            
    except Exception as e:
        st.error(f"Error processing download: {str(e)}")
    
def handle_download_page(share_hash):
    try:
        share_info = get_shared_file(share_hash)
        if not share_info:
            st.error("Invalid or expired download link")
            return

        file_path = share_info['file_path']
        if not os.path.exists(file_path):
            st.error("File no longer exists")
            return

        file_data = download_stored_file(file_path)
        if not file_data:
            return

        original_filename = share_info['original_filename']
        
        if original_filename.lower().endswith('.pdf'):
            base64_pdf = base64.b64encode(file_data).decode('utf-8')
            pdf_display = f'''
                <embed src="data:application/pdf;base64,{base64_pdf}" 
                       type="application/pdf" 
                       width="100%" 
                       height="800px" 
                       internalinstanceid="pdf-display">
            '''
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            try:
                df = pd.read_excel(io.BytesIO(file_data))
                
                st.markdown(f"### 📊 {original_filename}")
                
                search = st.text_input("🔍 Search in table:", "")
                
                if search:
                    mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
                    filtered_df = df[mask]
                else:
                    filtered_df = df
                
                st.markdown(f"**Total Rows:** {len(filtered_df)} | **Total Columns:** {len(filtered_df.columns)}")
                
                st.dataframe(
                    filtered_df,
                    use_container_width=True,
                    height=600
                )
                
                st.download_button(
                    "📥 Download Excel File",
                    file_data,
                    file_name=original_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
            except Exception as e:
                st.error(f"Error displaying Excel file: {str(e)}")
                st.download_button(
                    label="Download File",
                    data=file_data,
                    file_name=original_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    except Exception as e:
        st.error(f"Error handling download: {str(e)}")
        st.error(traceback.format_exc())

def verify_storage_setup():
    """Verify that storage is set up correctly"""
    try:
        if not os.path.exists('storage'):
            # st.error("Main storage directory is missing")
            return False
            
        shares_dir = 'storage/shares'
        if not os.path.exists(shares_dir):
            # st.error("Shares directory is missing")
            return False
                
        return True
    except Exception as e:
        st.error(f"Error verifying storage: {str(e)}")
        return False

def setup_storage():
    """Create necessary directories for file storage"""
    if not os.path.exists('storage'):
        os.makedirs('storage')
    
    if not os.path.exists('storage/uploads_tracking.xlsx'):
        df = pd.DataFrame(columns=['Username', 'Upload Date', 'Invoice Files', 'Excel Result', 'Path'])
        df.to_excel('storage/uploads_tracking.xlsx', index=False)



def save_uploaded_files(username, pdf_files, excel_data):
    """Save uploaded PDFs and Excel result"""
    try:
        # Create timestamp-based directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        user_dir = username.split('@')[0]
        save_path = f'storage/{user_dir}/{timestamp}'
        os.makedirs(save_path, exist_ok=True)
        
        pdf_names = []
        for pdf in pdf_files:
            pdf_path = f'{save_path}/{pdf.name}'
            with open(pdf_path, 'wb') as f:
                f.write(pdf.getvalue())
            pdf_names.append(pdf.name)
        
        excel_name = f'Data_Extract_{timestamp}.xlsx'
        excel_path = f'{save_path}/{excel_name}'
        excel_data.to_excel(excel_path, index=False)
        
        # Update tracking file
        tracking_df = pd.read_excel('storage/uploads_tracking.xlsx')
        new_row = {
            'Username': username,
            'Upload Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Invoice Files': ', '.join(pdf_names),
            'Excel Result': excel_name,
            'Path': save_path
        }
        tracking_df = pd.concat([tracking_df, pd.DataFrame([new_row])], ignore_index=True)
        tracking_df.to_excel('storage/uploads_tracking.xlsx', index=False)
        
        return save_path
        
    except Exception as e:
        st.error(f"Error saving files: {str(e)}")
        return None

def get_user_uploads(username):
    """Get all previous uploads for a user"""
    try:
        tracking_df = pd.read_excel('storage/uploads_tracking.xlsx')
        user_uploads = tracking_df[tracking_df['Username'] == username].copy()
        return user_uploads.sort_values('Upload Date', ascending=False)
    except Exception as e:
        st.error(f"Error retrieving uploads: {str(e)}")
        return pd.DataFrame()

def download_stored_file(file_path):
    """Read a stored file for downloading"""
    try:
        with open(file_path, 'rb') as f:
            return f.read()
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return None
def init_ocr():
    """Initialize OCR with optimized settings"""
    # Commenting out OCR initialization while keeping structure
    """
    try:
        from paddleocr import PaddleOCR
        ocr = PaddleOCR(
            use_angle_cls=False,
            lang='en',
            use_gpu=False,
            show_log=False
        )
        return ocr
    except Exception as e:
        st.error(f"Error initializing OCR: {str(e)}")
        return None
    """
    return None



st.markdown("""
    <style>

    
            
        .stButton>button {
            width: 100%;
            margin-top: 20px;
        }
        .main {
            padding: 2rem;
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 30px;
        }
        .stAlert {
            padding: 20px;
            margin: 10px 0;
        }
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .block-container{
            padding:2rem !important;
            padding-top: 5px !important;
        }
        .st-bi{
            color:#1A2F50 !important;
            
        }
        .st-key-refresh
        {
            color:#1A2F50;

            button{
                border:none;    
                background-color:#1A2F50;
                color:white;
                box-shadow: 2px 25px 25px rgba(0.5, 0.2, 0.2, 0.2); /* Proper shadow format */
            }
            button:hover{
             font-weight: bold;
                color:hsl(38.03deg 32.72% 57.45%);
            }
            
        }
        
        @import url('https://fonts.googleapis.com/css2?family=Epilogue:wght@300;400;600&display=swap');

        html, body {
            font-family: 'Epilogue', sans-serif;
        }
            
        div[data-testid="stFileUploaderDropzoneInstructions"] small {
         display: none !important;
        }
            
        div.st-key-extractinfofromdocs{
            button{
                border:none;  
                background-color:#1A2F50;
                color:white;
                box-shadow: 2px 25px 25px rgba(0.5, 0.2, 0.2, 0.2); 
            }
            button:hover{
                 color:hsl(38.03deg 32.72% 57.45%);
            }
        }
        .st-key-save_changes_existing{
            display:none !important; 
            }    
            
             
    </style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False
if 'username' not in st.session_state: 
    st.session_state.username = None

DEFAULT_PASSWORD = '12345'
USER_TRACKING_FILE = 'user_tracking.xlsx'
  
def validate_email(email): 
    return email.lower().endswith('medlab@akigroup.com') or email.endswith('Sajid')

def get_shared_file(share_hash):
    """Retrieve shared file information"""
    try:
        share_file = f'storage/shares/{share_hash}.json'
        if not os.path.exists(share_file):
            return None
            
        with open(share_file, 'r') as f:
            share_info = json.load(f)
            
        expiry_date = datetime.strptime(share_info['expiry_date'], '%Y-%m-%d')
        if datetime.now() > expiry_date:
            os.remove(share_file)  
            return None
            
        return share_info
    
    except Exception as e:
        st.error(f"Error retrieving shared file: {str(e)}")
        return None



def handle_excel_upload():
    """
    Handle Excel file uploads and display the content within the application
    """
    st.markdown("### 📊 Upload Existing Excel File")
    
    uploaded_excel = st.file_uploader(
        "Upload your Excel file",
        type=["xlsx", "xls"],
        help="Upload an existing Excel file with ASN data",
        key="excel_uploader"
    )
    
    if uploaded_excel:
        try:
            file_info_col1, file_info_col2 = st.columns(2)
            
            with file_info_col1:
                st.success(f"✅ Successfully uploaded: {uploaded_excel.name}")
                file_size = round(len(uploaded_excel.getvalue()) / 1024, 2)
                st.info(f"File size: {file_size} KB")
            
            with file_info_col2:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                st.info(f"Upload time: {timestamp}")
            
            excel_data = uploaded_excel.read()
            
            with st.spinner("Processing Excel file..."):
                df = enhanced_display_excel_native(excel_data)
            
            if df is not None:
                # Data operations section
                # st.markdown("### 🔧 Data Operations")
                
                # operations_col1, operations_col2 = st.columns(2)
                
                # with operations_col1:
                    # Add option to save this as the edited_df for the current session
                #     if st.button("📌 Use This Excel for Current Session", key="use_excel"):
                #         # st.session_state.edited_df = df.copy()
                #         st.session_state.uploaded_pdfs = []  # Clear any uploaded PDFs
                        
                #         # Add a visual effect to show processing
                #         success_message = st.empty()
                #         progress = st.progress(0)
                #         for i in range(100):
                #             time.sleep(0.01)
                #             progress.progress(i + 1)
                        
                #         success_message.success("Excel data is now available in the current session!")
                #         time.sleep(1)  # Allow user to see the message
                #         st.rerun()
                
                # with operations_col2:
                #     # Add button to edit in the main tab
                #     if st.button("✏️ Edit in the Main Tab", key="edit_excel"):
                #         st.session_state.edited_df = df.copy()
                #         st.session_state.grid_key = f'grid_{datetime.now().strftime("%Y%m%d%H%M%S")}'
                #         st.info("Switching to the main tab for editing...")
                #         time.sleep(1)
                #         st.rerun()
                
                st.markdown("### 📥 Download Options")
                
                st.download_button(
                    "📄 Download Original Excel",
                    excel_data,
                    file_name=uploaded_excel.name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_original_excel"
                )
                
        except Exception as e:
            st.error(f"Error processing Excel file: {str(e)}")
            st.error(traceback.format_exc())
    else:
        st.info("Please upload an Excel file to view its content")
        
        with st.expander("ℹ️ Expected Excel Format"):
            st.markdown("Your Excel file should contain the following columns:")
            expected_columns = [
                'PO Number', 'Item Code', 'Description', 'UOM', 'Quantity', 
                'Lot Number', 'Expiry Date', 'Mfg Date', 'Invoice No',
                'Unit Price', 'Total Price', 'Country', 'HS Code',
                'Invoice Date', 'Customer No', 'Payer Name', 'Currency',
                'Supplier', 'Invoice Total', 'VAT', 'Line Number', 'Costing Number'
            ]
            
            columns_per_row = 3
            for i in range(0, len(expected_columns), columns_per_row):
                cols = st.columns(columns_per_row)
                for j in range(columns_per_row):
                    if i + j < len(expected_columns):
                        cols[j].markdown(f"• **{expected_columns[i + j]}**")

def validate_excel_columns(df):
    """
    Validate that the uploaded Excel file contains the expected columns
    """
    expected_columns = [
        'PO Number', 'Item Code', 'Description', 'UOM', 'Quantity', 
        'Lot Number', 'Expiry Date', 'Mfg Date', 'Invoice No',
        'Unit Price', 'Total Price', 'Country', 'HS Code',
        'Invoice Date', 'Customer No', 'Payer Name', 'Currency',
        'Supplier', 'Invoice Total', 'VAT', 'Line Number', 'Costing Number'
    ]
    
    missing_columns = [col for col in expected_columns if col not in df.columns]
    
    extra_columns = [col for col in df.columns if col not in expected_columns]
    
    if missing_columns:
        st.warning(f"⚠️ The Excel file is missing the following expected columns: {', '.join(missing_columns)}")
    
    if extra_columns:
        st.info(f"ℹ️ The Excel file contains additional columns: {', '.join(extra_columns)}")
    
    return len(missing_columns) == 0  




def enhanced_display_excel_native(excel_data):
    """Enhanced version of display_excel_native with column validation and editing capabilities"""
    try:
        df = pd.read_excel(io.BytesIO(excel_data))
        
        columns_valid = validate_excel_columns(df)
        
        excel_file = io.BytesIO(excel_data)
        xl = pd.ExcelFile(excel_file)
        sheet_names = xl.sheet_names
        
        if len(sheet_names) > 1:
            selected_sheet = st.selectbox("Select Sheet:", sheet_names)
            df = pd.read_excel(excel_file, sheet_name=selected_sheet)
            columns_valid = validate_excel_columns(df)
        
        search_key = f"excel_search_{id(excel_data)}"
        search = st.text_input("🔍 Search in table:", key=search_key)
        
        if search:
            if ":" in search:
                col_name, filter_value = search.split(":", 1)
                col_name = col_name.strip()
                filter_value = filter_value.strip()
                
                if col_name in df.columns:
                    mask = df[col_name].astype(str).str.contains(filter_value, case=False)
                    filtered_df = df[mask]
                    st.info(f"Filtering by column: '{col_name}' containing '{filter_value}'")
                else:
                    mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
                    filtered_df = df[mask]
            else:
                mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
                filtered_df = df[mask]
        else:
            filtered_df = df
        
        st.markdown(f"**Total Rows:** {len(filtered_df)} | **Total Columns:** {len(filtered_df.columns)}")
        
        editor_key = f"excel_editor_{hash(str(filtered_df.head(5)))}"
        
        edited_df = st.data_editor(
            filtered_df,
            use_container_width=True,
            num_rows="dynamic",
            key=editor_key,
            height=600,
            column_config={
                col: st.column_config.Column(
                    width="auto",
                    help=f"Column: {col}"
                ) for col in filtered_df.columns
            }
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                edited_df.to_excel(writer, index=False)
            
            st.download_button(
                "📥 Download Edited Excel",
                buffer.getvalue(),
                file_name="edited_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"download_edited_excel_{id(excel_data)}"
            )
        
        with col2:
            if st.button("💾 Save Changes", key=f"save_excel_changes_{id(excel_data)}"):
                st.success("Changes saved! You can now use this data in the main session.")
                return edited_df
        
        return edited_df
    except Exception as e:
        st.error(f"Error displaying Excel file: {str(e)}")
        st.error(traceback.format_exc())
        return None





def init_user_tracking():
    try:
        if not os.path.exists(USER_TRACKING_FILE):
            df = pd.DataFrame(columns=[
                'User ID',
                'Username',
                'Upload Time',
                'Files Uploaded',
                'Rows Uploaded'
            ])
            try: 
                df.to_excel(USER_TRACKING_FILE, index=False)
            except PermissionError:
                st.warning("Warning: Could not create tracking file. Data will be cached in session.")
                st.session_state.user_tracking = df

    except Exception as e:
        st.error(f"Error initializing user tracking: {str(e)}")
        st.session_state.user_tracking = pd.DataFrame(columns=[
            'User ID',
            'Username',
            'Upload Time',
            'Files Uploaded',
            'Rows Uploaded'
        ])
            

def display_history_tab():
    st.markdown("### 📂 Previous Uploads")
    user_uploads = get_user_uploads(st.session_state.username)
    
    if not user_uploads.empty:
        for idx, row in user_uploads.iterrows():
            session_id = f"session_{idx}"
            
            with st.expander(f"Upload from {row['Upload Date']}"):
                st.write(f"**Invoice Files:** {row['Invoice Files']}")
                
                pdf_col, excel_col, share_col = st.columns(3)
                
                with pdf_col:
                    st.markdown("**📄 Invoice PDFs:**")
                    for pdf_idx, pdf_name in enumerate(row['Invoice Files'].split(', ')):
                        pdf_path = os.path.join(row['Path'], pdf_name)
                        if os.path.exists(pdf_path):
                            pdf_key = f"pdf_{session_id}_{pdf_idx}_{hash(pdf_name)}"
                            st.download_button(
                                f"📥 {pdf_name}",
                                download_stored_file(pdf_path),
                                file_name=pdf_name,
                                mime="application/pdf",
                                key=pdf_key
                            )
                
                with excel_col:
                    st.markdown("**📊 Excel Result:**")
                    excel_path = os.path.join(row['Path'], row['Excel Result'])
                    if os.path.exists(excel_path):
                        excel_key = f"excel_{session_id}_{hash(row['Excel Result'])}"
                        st.download_button(
                            f"📥 {row['Excel Result']}",
                            download_stored_file(excel_path),
                            file_name=row['Excel Result'],
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=excel_key
                        )
                
                with share_col:
                    st.markdown("**🔗 Share Files:**")
                    share_key = f"share_{session_id}"
                    if st.button("Generate Links", key=share_key):
                        share_links = []
                        
                        for pdf_name in row['Invoice Files'].split(', '):
                            pdf_path = os.path.join(row['Path'], pdf_name)
                            if os.path.exists(pdf_path):
                                pdf_link = generate_share_link(pdf_path)
                                if pdf_link:
                                    share_links.append((pdf_name, pdf_link))
                        
                        excel_path = os.path.join(row['Path'], row['Excel Result'])
                        if os.path.exists(excel_path):
                            excel_link = generate_share_link(excel_path)
                            if excel_link:
                                share_links.append((row['Excel Result'], excel_link))
                        
                        if share_links:
                            st.markdown("**Generated Links:**")
                            for link_idx, (file_name, link) in enumerate(share_links):
                                link_container_key = f"link_container_{session_id}_{link_idx}"
                                with st.container(key=link_container_key):
                                    st.text(file_name)
                                    st.code(link)
                                    copy_key = f"copy_{session_id}_{link_idx}"
                                    st.button(
                                        "📋 Copy Link",
                                        key=copy_key,
                                        on_click=lambda l=link: st.write(f"```{l}```")
                                    )
                                    st.markdown("---")
    else:
        st.info("No previous uploads found")

def update_user_tracking(username, files_uploaded=0, rows_processed=0):
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        df = None
        
        try:
            if os.path.exists(USER_TRACKING_FILE):
                df = pd.read_excel(USER_TRACKING_FILE)
            else:
                df = pd.DataFrame(columns=[
                    'User ID',
                    'Username',
                    'Upload Time',
                    'Files Uploaded',
                    'Rows Processed'
                ])
        except Exception as e:
            st.warning(f"Could not read tracking file: {str(e)}")
            df = pd.DataFrame(columns=[
                'User ID',
                'Username',
                'Upload Time',
                'Files Uploaded',
                'Rows Processed'
            ])

        if df is not None and not df.empty:
            user_id = df['User ID'].max() + 1
        else:
            user_id = 1

        new_row = pd.DataFrame({
            'User ID': [user_id],
            'Username': [username],
            'Upload Time': [current_time],
            'Files Uploaded': [files_uploaded],
            'Rows Processed': [rows_processed]
        })

        df = pd.concat([df, new_row], ignore_index=True)

        try:
            df.to_excel(USER_TRACKING_FILE, index=False)
            if files_uploaded > 0:
                st.success(f"""File(s) uploaded successfully:
                - File(s) uploaded: {files_uploaded}
                - Row(s) processed: {rows_processed}""")
        except Exception as e:
            st.warning(f"Could not save tracking file: {str(e)}")
            st.session_state['tracking_df'] = df
            if files_uploaded > 0:
                st.info(f"""Upload tracked (temporarily saved):
                - Files uploaded: {files_uploaded}
                - Rows processed: {rows_processed}""")

    except Exception as e:
        st.error(f"User tracking update error: {str(e)}")


def is_scanned_pdf(pdf_path):
    """Check if PDF is scanned by attempting to extract text"""
    try:
        with fitz.open(pdf_path) as pdf:
            text_content = ""
            for page in pdf:
                text_content += page.get_text() or ""

            if len(text_content.strip()) < 100:
                st.info("We are working on it now") 
                return True
            return False
    except Exception as e:
        st.error(f"Error checking PDF type: {str(e)}")
        return True



def process_invoice_lines(invoice_info, costing_number=""):
    """
    Process invoice information lines with standardized headers
    """
    try:
        header_mappings = {
            'Customer Number': 'Customer No',
            'Customer No.': 'Customer No',
            'Supplier Name': 'Supplier',
            'Total VAT': 'VAT',
            'Total VAT or VAT': 'VAT',
            'Total Amount of the Invoice': 'Invoice Total',
            'Payer Name': 'Payer Name',
            'Date of Invoice': 'Invoice Date',
            'Manufacturing Date': 'Mfg Date',
            'Manufacture Date': 'Mfg Date',
            'Production Date': 'Mfg Date',
            'Prod Date': 'Mfg Date',
            'Prod. Date': 'Mfg Date',
            'Date of Manufacture': 'Mfg Date',
            'DOM': 'Mfg Date',
            'Manufactured On': 'Mfg Date',
            'Manuf. Date': 'Mfg Date'
        }

        standard_headers = [
            'PO Number', 'Item Code', 'Description', 'UOM', 'Quantity',
            'Lot Number', 'Expiry Date', 'Mfg Date', 'Invoice No',
            'Unit Price', 'Total Price', 'Country', 'HS Code',
            'Invoice Date', 'Customer No', 'Payer Name', 'Currency',
            'Supplier', 'Invoice Total', 'VAT', 'Line Number'
        ]

        if 'Costing Number' not in standard_headers:
            standard_headers.append('Costing Number')

        lines = [line.strip() for line in invoice_info.split('\n')]
        valid_lines = []
        
        for line in lines:
            if not line:
                continue
            if '--' in line and '|' not in line:
                valid_lines.append(line)
                continue
            if set(line).issubset({'-', ' '}):
                continue
            if '|' in line:
                cleaned_cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                valid_lines.append('|'.join(cleaned_cells))

        headers = None
        data_rows = []
        raw_headers = None
        
        for line in valid_lines:
            if '--' in line and '|' not in line:
                continue
                
            if '|' in line:
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                
                if headers is None:
                    raw_headers = cells
                    headers = standard_headers
                    # st.write(f"DEBUG - Original headers: {raw_headers}")
                    # st.write(f"DEBUG - Standardized headers: {headers}")
                else:
                    data_dict = {}
                    for i, cell in enumerate(cells):
                        if i < len(raw_headers):
                            data_dict[raw_headers[i]] = cell

                    standardized_row = []
                    for header in headers[:-1]:
                        value = ''
                        # Check mapped header names first
                        mapped_found = False
                        for raw_key, std_key in header_mappings.items():
                            if std_key == header and raw_key in data_dict:
                                value = data_dict[raw_key]
                                mapped_found = True
                                break
                        
                        if not mapped_found and header in data_dict:
                            value = data_dict[header]
                        
                        standardized_row.append(value)

                    standardized_row.append(costing_number)
                    data_rows.append(standardized_row)

        if headers and data_rows:
            for i, row in enumerate(data_rows):
                if len(row) != len(headers):
                    # st.write(f"DEBUG - Row {i} length mismatch: {len(row)} vs {len(headers)}")
                    # st.write(f"DEBUG - Row data: {row}")
                    # Pad or trim row to match header length
                    if len(row) < len(headers):
                        row.extend([''] * (len(headers) - len(row)))
                    else:
                        data_rows[i] = row[:len(headers)]

        return headers, data_rows
        
    except Exception as e:
        st.error(f"Error in process_invoice_lines: {str(e)}")
        st.error(traceback.format_exc())
        return None, None



def count_processed_rows(invoice_info):
    """
    Count actual data rows, excluding separators and headers
    """
    try:
        lines = [line.strip() for line in invoice_info.split('\n')]
        
        data_rows = 0
        header_found = False
        
        for line in lines:
            if not line or set(line.replace('|', '')).issubset({'-', ' '}):
                continue
                
            if not header_found:
                header_found = True
                continue
                
            data_rows += 1
            
        return data_rows
        
    except Exception as e:
        st.error(f"Error counting processed rows: {str(e)}")
        return 0



def extract_text_from_scanned_pdf(pdf_path):
    """Extract text from scanned PDF using OCR methods"""
    """
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # First try with doctr
                try:
                    doc = DocumentFile.from_pdf(pdf_path)
                    doctr_model = ocr_predictor(det_arch="db_resnet50", reco_arch="crnn_vgg16_bn", pretrained=True)
                    result = doctr_model(doc)
                    
                    # Extract text from doctr result
                    extracted_text = []
                    for page in result.pages:
                        for block in page.blocks:
                            for line in block.lines:
                                for word in line.words:
                                    extracted_text.append(word.value)
                    
                    if extracted_text:
                        st.success("Successfully extracted text using doctr")
                        return " ".join(extracted_text)
                    
                except Exception as doctr_error:
                    st.warning(f"Doctr extraction failed, falling back to PaddleOCR: {str(doctr_error)}")
                
                # Initialize PaddleOCR with English language and no angle classification
                ocr = PaddleOCR(use_angle_cls=False, lang='en')
                
                # Open PDF with PyMuPDF
                pdf_document = fitz.open(pdf_path)
                all_results = []
                total_pages = len(pdf_document)
                
                # Process each page with progress bar
                progress_bar = st.progress(0)
                
                for page_num in range(total_pages):
                    try:
                        # Get page and convert to image
                        page = pdf_document[page_num]
                        pix = page.get_pixmap(alpha=False)
                        
                        # Convert to numpy array
                        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                            pix.height, pix.width, 3 if pix.n >= 3 else 1
                        )
                        
                        if img_array.shape[-1] == 1:
                            img_array = np.repeat(img_array, 3, axis=-1)
                        
                        # Run OCR
                        result = ocr.ocr(img_array, cls=False)
                        
                        if result:
                            page_text = []
                            for line in result:
                                if isinstance(line, (list, tuple)):
                                    for item in line:
                                        if isinstance(item, (list, tuple)) and len(item) >= 2:
                                            text = item[1][0] if isinstance(item[1], (list, tuple)) else item[1]
                                            page_text.append(str(text))
                            
                            all_results.extend(page_text)
                    
                    except Exception as ocr_error:
                        st.warning(f"Error in OCR processing for page {page_num + 1}: {str(ocr_error)}")
                        continue
                    
                    progress_bar.progress((page_num + 1) / total_pages)
                    gc.collect()
                
                pdf_document.close()
                progress_bar.empty()
                
                if all_results:
                    return "\n".join(all_results)
                else:
                    st.error("No text was extracted from the PDF")
                    return None
                    
            except Exception as e:
                st.error(f"PDF processing error: {str(e)}")
                return None
            
    except Exception as e:
        st.error(f"OCR processing error: {str(e)}")
        return None
    """
    st.info("We are working on it now")
    return None


def check_shared_file():
    """Handle shared file viewing and downloading"""
    try:
        share_hash = st.query_params.get('share')
        
        if share_hash:
            share_info = get_shared_file(share_hash)
            if share_info:
                file_path = share_info['file_path']
                if os.path.exists(file_path):
                    file_data = download_stored_file(file_path)
                    if file_data:
                        file_name = os.path.basename(file_path)
                        st.markdown(f"### 📄 File: {file_name}")
                        
                        if file_name.lower().endswith('.pdf'):
                            st.info("Loading PDF viewer... If the viewer doesn't load, you can use the download options.")
                            display_pdf(file_data)
                        else:
                            try:
                                df = pd.read_excel(io.BytesIO(file_data))
                                
                                search = st.text_input("🔍 Search in table:", key="excel_search")
                                if search:
                                    mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
                                    df = df[mask]
                                
                                st.markdown(f"**Total Rows:** {len(df)} | **Total Columns:** {len(df.columns)}")
                                
                                st.dataframe(
                                    df,
                                    use_container_width=True,
                                    height=600
                                )
                                
                                st.download_button(
                                    "📥 Download Excel File",
                                    file_data,
                                    file_name=file_name,
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                            except Exception as excel_error:
                                st.error(f"Error displaying Excel file: {str(excel_error)}")
                                st.download_button(
                                    label="Download File",
                                    data=file_data,
                                    file_name=file_name,
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                    else:
                        st.error("Unable to read the shared file.")
                else:
                    st.error("The shared file no longer exists.")
            else:
                st.error("This share link has expired or is invalid.")
    except Exception as e:
        st.error(f"Error processing shared file: {str(e)}")
        st.error(traceback.format_exc())

def login_page():
    """Display a clean login page that matches your current design but adds the company logo"""
    
    st.markdown("""
    <style>
        /* Add space at the top of the page */
        .main > div:first-child {
            padding-top: 20px;
        }
        
        /* Login button styling */
        .stButton > button {
            width: 100%;
            border-radius: 4px;
            background-color: #f0f2f6;
            color: #262730;
            font-weight: 400;
            border: 1px solid #d2d2d2;
            padding: 10px;
            font-size: 14px;
        }
        
        /* Footer styling */
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 15px;
            background-color: #f9f9f9;
            border-top: 1px solid #eaeaea;
            display: flex;
            justify-content: space-between;
            font-size: 14px;
            color: #5f6368;
        }
        
        /* Container for main content */
        .content-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* Logo styling */
        .logo-area {
            display: flex;
            align-items: center;
            justify-content: flex-end;  /* Align to right */
            margin-bottom: 30px;
        }
        
        .app-title {
            font-size: 24px;
            font-weight: 600;
            color: #333;
            margin-right: 10px;  /* Changed from margin-left to margin-right */
        }
        
        /* Logo image specific styling */
        .logo-image {
            text-align: right;
            display:none;
        }
    </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        col1, col2 = st.columns([5,1])
        
        with col1:
            st.markdown("<h1 style='text-align: left; margin-left: 120px;'>AKI Agentic AI Intelligent Document Processor</h1>", unsafe_allow_html=True)

        # with col2:
        #     if os.path.exists("assets/aki.png"):
        #         st.image("assets/aki.png", width=170)  
        #     else:
        #         st.markdown("<div class='logo-image'>📁</div>", unsafe_allow_html=True)
    
    
    with st.container():
        col1, col2, col3 = st.columns([1, 10, 1])
        with col2:
            username = st.text_input("AKI Username", placeholder="your.email@akigroup.com", key="login_username_field")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password_field")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            login_button = st.button("Login", key="login_button")
            
            st.markdown("<div style='text-align: center; margin-top: 15px; font-size: 0.9rem; color: #666;'>Please enter your AKI credentials to access the system</div>", unsafe_allow_html=True)
        
            if login_button:
                if not username or not password:
                    st.error("Please fill in all fields")
                    return
                
                if not validate_email(username):
                    st.error("Username must end with @akigroup.com")
                    return
                
                if username == 'admin@akigroup.com':
                    if password != DEFAULT_PASSWORD:
                        st.error("Invalid admin password")
                        return
                elif password != DEFAULT_PASSWORD:
                    st.error("Invalid password")
                    return
                
                st.session_state.logged_in = True
                st.session_state.username = username
                update_user_tracking(username)
                
                success_placeholder = st.empty()
                success_placeholder.success("Login successful! Redirecting...")
                
                progress = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress.progress(i + 1)
                
                progress.empty()
                success_placeholder.empty()
                st.rerun()
    
    st.markdown("""
    <div class="footer">
        <div>© 2025 Al Khayyat Investment</div>
        <div>Need help? Contact: <a href="mailto:support@akigroup.com">support@akigroup.com</a></div>
    </div>
    """, unsafe_allow_html=True)


def extract_text_pdf(pdf_path):
    """Extract text from PDF, handling both scanned and machine-readable PDFs"""
    if is_scanned_pdf(pdf_path):
        st.info("We are working on scanned PDFs. Please wait...")
        return None
    else:
        try:
            with fitz.open(pdf_path) as pdf:
                unique_pages = {}
                for page_num, page in enumerate(pdf):
                    page_text = page.get_text()
                    content_hash = hash(page_text)
                    if content_hash not in unique_pages:
                        unique_pages[content_hash] = page_text
                return "\n".join(unique_pages.values())
        except Exception as e:
            st.error(f"Error extracting text: {str(e)}")
            return None
            

def format_markdown_table(headers, data):
    """
    Create a properly formatted Markdown table with consistent separator line
    """
    table = [f"| {' | '.join(headers)} |"]
    
    separator = [f"|{'|'.join('-' * (len(header) + 2) for header in headers)}|"]
    
    data_rows = [f"| {' | '.join(row)} |" for row in data]
    
    return '\n'.join(table + separator + data_rows)



def using_groq(text: str):
    """
    Process invoice text through Groq API with intelligent chunking for large documents.
    
    Args:
        text (str): The text extracted from the invoice PDF
        
    Returns:
        str: The processed invoice information with structured data
    """
    import re
    
    if not text:
        return None
    
    estimated_tokens = len(text) // 4
    
    prompt_template = """Extract ALL invoice data without skipping ANY item and FILL EVERY FIELD. Empty cells WILL cause FAILURE.

{text_content}

### Mandatory Fields (Every row must have values):
   - PO Number: Order Number or Purchase Order fields. 
     IMPORTANT: Remove any text like "MDS", "-MDS", "/MDS" after the number
     If not found, use "-"
   - Item Code: If missing, use "ITEM" + line number
   - Description: If missing, use "Product Line " + line number
   - UOM: Unit of Measure 
   - Quantity: or Quantity Shipped
   - Lot Number: Example: "Batch/serial Nr 272130" means lot number is "272130"
                 IMPORTANT: If multiple batches/lots exist for the same item, CREATE SEPARATE ROWS for each batch
                 Only use "N/A" if confirmed missing after thorough search
   - Expiry Date: use "-" if missing, format as DD-MM-YYYY
                  IMPORTANT: If multiple expiry dates exist, CREATE SEPARATE ROWS with matching lot numbers
   - Manufacturing Date or Mfg Date: Only use "N/A" if confirmed missing after thorough search
   - Invoice No: MUST be found - look in header
   - Unit Price: Default to Total Price if missing
   - Total Price: Default to Unit Price × Quantity if missing
   - Country: Convert codes to full names (e.g., IE → Ireland).
   - HS Code: Default "-" if missing
   - Invoice Date: Extract from header or near invoice number (format: DD-MM-YYYY)
   - Customer No: Extract from "Customer Nr" fields or fallback to company code
   - Payer Name: ALWAYS exactly "ALPHAMED GENERAL TRADING LLC." (no exceptions)
   - Currency: Use "EUR" for European suppliers, "USD" for USA, "THB" for Thailand
   - Supplier: MUST find the company name from letterhead/invoice header
   - Invoice Total: Sum all line totals if not explicitly stated
   - VAT: Look for VAT percentage or amount - use "0" if not found
   
CRITICAL:
- MULTIPLE LOT HANDLING:
    - When an item has multiple batches/lots listed (like "Batch: 37465YQ" and "Batch: 37580YQ"), you MUST create separate rows for each batch
    - Example:
    Lot Number: 23229017
                23231017
    Expiry Date: 01-08-2025
                 01-08-2025 
- SEARCH THE ENTIRE DOCUMENT for information, not just the main table. Many invoices have detailed sections below the main table with additional information about each line item (batch numbers, country of origin, manufacturing dates, etc.)
- MAKE SURE to not extract any thing from packing list like every thing "Treatment License"
- For quantity, If "Pack Factor" or "Line has X packs" is present, multiply the pack count by the pack factor.
  For example, "Line has 522 packs" with "Pack Factor: 2" means 522 × 2 = 1044, not 522.
   
CRITICAL FIELD COMPLETION REQUIREMENT:

DO NOT SKIP ANY ITEMS OR ENTRIES. You must extract EVERY SINGLE LINE ITEM from the invoice, even if they seem similar to others.
If you see multiple items with the same or similar product descriptions but different item codes, PO numbers, or quantities, 
you MUST include ALL of them as separate entries in your output.

Rules for Missing Data::
   - Line Number: extract Line number from invoices example :(10, 20, etc) if missing use row sequence (1, 2, 3...) if missing
   - If data is completely missing: Use "N/A".
   - Never leave any cell blank—search the entire invoice if needed

THIS IS A FIRM REQUIREMENT: Every single cell in every single row MUST have a value - NEVER leave anything blank. If you don't see information in the table, SEARCH THE ENTIRE INVOICE TEXT.
Use "N/A" only as a last resort when information truly cannot be found.

SPECIFIC EXTRACTION RULES:
1. Item Code: Item Code: Extract only the product/item code (4-8 digits). Ignore order or delivery note numbers.

### Validation Checks:
- Ensure correct field identification.
- Review multilingual labels.
- Avoid misclassifying reference numbers as item codes.

### Final Output:
- Complete table—every field filled.
- Verify all values before finalizing.e table with ALL fields populated for EVERY row and VERIFY each field is appropriately filled before finalizing.
{chunk_directive}
"""
    
    if estimated_tokens < 32000:
        prompt = prompt_template.format(
            text_content=text,
            chunk_directive=""
        )
        
        try:
            completion = openai_client.chat.completions.create(
                model="gpt-4o",  
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant who extracts detailed and precise information from invoice texts. Ensure no data is missed and follow the instructions exactly."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1
            )
            return completion.choices[0].message.content
        except Exception as e:
            st.error(f"Error in API call: {str(e)}")
            return None
    
    st.info(f"Processing large document (est. {estimated_tokens} tokens) in chunks...")
    
    chunks = split_text_into_chunks(text, chunk_size=4000)
    
    progress_bar = st.progress(0)
    chunk_status = st.empty()
    
    all_results = []
    
    for i, chunk in enumerate(chunks):
        chunk_status.text(f"Processing chunk {i+1}/{len(chunks)} with ~{len(chunk)//4} tokens")
        
        chunk_directive = f"""
IMPORTANT: This is CHUNK {i+1} of {len(chunks)} from a larger document.
Focus only on extracting information from THIS CHUNK.
In your response, ONLY include the table with extracted data in pipe-delimited format.
DO NOT include any explanations or notes.
"""
        
        prompt = prompt_template.format(
            text_content=chunk,
            chunk_directive=chunk_directive
        )
        
        try:
            # Process the chunk
            completion = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant who extracts detailed and precise information from invoice texts. Ensure no data is missed from this chunk and follow the instructions exactly."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1
            )
            
            chunk_result = completion.choices[0].message.content
            
            if chunk_result:
                all_results.append(chunk_result)
            
        except Exception as e:
            st.error(f"Error processing chunk {i+1}: {str(e)}")
        
        progress_bar.progress((i + 1) / len(chunks))
    
    progress_bar.empty()
    chunk_status.empty()
    
    if not all_results:
        return None
    
    combined_result = combine_chunked_results(all_results)
    st.success("Successfully processed document in chunks")
    
    return combined_result


def split_text_into_chunks(text, chunk_size=4000):
    """
    Split text into chunks of approximately chunk_size tokens, trying to maintain
    logical breaks at paragraph boundaries where possible.
    
    Args:
        text (str): Text to split
        chunk_size (int): Approximate chunk size in tokens (estimated by chars/4)
        
    Returns:
        list: List of text chunks
    """
    import re
    
    token_ratio = 4
    
    paragraphs = re.split(r'\n\s*\n', text)
    
    chunks = []
    current_chunk = []
    current_chunk_size = 0
    
    for paragraph in paragraphs:
        if not paragraph.strip():
            continue
        
        paragraph_size = len(paragraph) // token_ratio
        
        if paragraph_size > chunk_size:
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)
            
            for sentence in sentences:
                sentence_size = len(sentence) // token_ratio
                
                if current_chunk_size + sentence_size > chunk_size and current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = [sentence]
                    current_chunk_size = sentence_size
                else:
                    current_chunk.append(sentence)
                    current_chunk_size += sentence_size
        
        else:
            if current_chunk_size + paragraph_size > chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [paragraph]
                current_chunk_size = paragraph_size
            else:
                current_chunk.append(paragraph)
                current_chunk_size += paragraph_size
    
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
    
    return chunks


def standardize_headers(headers):
    """
    Standardize header names across different PDFs
    """
    header_mappings = {
        'Customer Number': 'Customer No',
        'Customer No.': 'Customer No',
        'Supplier Name': 'Supplier',
        'Total VAT': 'VAT',
        'Total VAT or VAT': 'VAT',
        'Total Amount of the Invoice': 'Invoice Total',
        'Payer Name': 'Payer Name', 
        'Date of Invoice': 'Invoice Date'  
    }

    standard_headers = [
        'PO Number', 'Item Code', 'Description', 'UOM', 'Quantity',
        'Lot Number', 'Expiry Date', 'Mfg Date', 'Invoice No',
        'Unit Price', 'Total Price', 'Country', 'HS Code',
        'Invoice Date', 'Customer No', 'Payer Name', 'Currency',
        'Supplier', 'Invoice Total', 'VAT', 'Line Number'
    ]

    if 'Costing Number' not in standard_headers:
        standard_headers.append('Costing Number')

    standardized = []
    for header in headers:
        if header in header_mappings:
            standardized.append(header_mappings[header])
        else:
            standardized.append(header)

    for header in standard_headers:
        if header not in standardized:
            standardized.append(header)

    return standard_headers  




# def main_app():
#     # st.title("🗂️ ASN Project - Data Extraction - AKI Company")
#     display_branding()  # Add this line to display the logo and branding
    
#     if st.session_state.username == 'admin@akigroup.com':
#         tab1, tab2, tab3, tab4 = st.tabs(["Upload & Process", "Excel Upload", "History", "User Tracking"])
#     else:
#         tab1, tab2, tab3 = st.tabs(["Upload & Process", "Excel Upload", "History"])
    
#     with tab1:
#         st.markdown(f"Welcome {st.session_state.username} to AKI's AI tool to extract data from documents.")
#         action_col1, action_col2, action_col3 = st.columns([1, 1, 1])

#         with action_col1:
#             if st.button("🔄 Process Next Document", key="refresh"):
#                 refresh_page()
    
#         with action_col3:
#             if st.button("🚪 Logout", key="logout"):
#                 st.session_state.logged_in = False
#                 st.session_state.username = None
#                 st.rerun()

#         # Initialize session state variables
#         if 'edited_df' not in st.session_state:
#             st.session_state.edited_df = None
#         if 'saved_df' not in st.session_state:
#             st.session_state.saved_df = None
#         if 'processing_complete' not in st.session_state:
#             st.session_state.processing_complete = False
#         # if 'costing_numbers' not in st.session_state:
#         #     st.session_state.costing_numbers = {}
#         if 'uploaded_pdfs' not in st.session_state:
#             st.session_state.uploaded_pdfs = []
#         if 'grid_key' not in st.session_state:
#             st.session_state.grid_key = 'data_editor_1'


        
#         col1, col2 = st.columns(2)

        
#         with col1:
#             uploaded_pdfs = st.file_uploader(
#                 "📄 Upload PDF Invoices",
#                 type=["pdf"],
#                 accept_multiple_files=True,
#                 help="You can upload multiple Invoice files for different suppliers",
#                 key=f"file_uploader_{st.session_state.get('refresh_timestamp', '')}"
#             )

#         if uploaded_pdfs:
#             st.session_state.uploaded_pdfs = uploaded_pdfs

#         with col2:
#             excel_file = st.text_input(
#                 "📊 Excel File Name",
#                 value="ASN_Result.xlsx",
#                 help="Enter the name for your output ASN file"
#             )

#         pdfs_to_process = st.session_state.uploaded_pdfs or uploaded_pdfs

#         if pdfs_to_process:
#             if st.session_state.edited_df is not None:
#                 try:
#                     st.markdown("### 📝 Extracted and Edited Data")
                    
#                     # Add search functionality before data editor
#                     search_query = st.text_input("🔍 Search in table:", key=f"search_input_{st.session_state.grid_key}")
                    
#                     # Get the data to display
#                     display_df = st.session_state.edited_df.copy()
                    
#                     # Apply search filter if there's a query
#                     if search_query:
#                         mask = display_df.astype(str).apply(
#                             lambda x: x.str.contains(search_query, case=False)
#                         ).any(axis=1)
#                         display_df = display_df[mask]
                    
#                     # Create the editable dataframe
#                     edited_df = st.data_editor(
#                         display_df,
#                         use_container_width=True,
#                         num_rows="dynamic",
#                         height=600,
#                         key=st.session_state.grid_key,
#                         column_config={
#                             col: st.column_config.Column(
#                                 width="auto",
#                                 help=f"Edit {col}"
#                             ) for col in display_df.columns
#                         }
#                     )
                    
#                     # Update session state with edited data
#                     st.session_state.edited_df = edited_df
                    
#                     # Display data info
#                     st.markdown(f"**Total Rows:** {len(edited_df)} | **Total Columns:** {len(edited_df.columns)}")
                    
#                     # Save Changes Button
#                     if st.button("💾 Save Table Changes", key="save_changes_existing"):
#                         st.session_state.saved_df = edited_df.copy()
#                         # Save files to storage
#                         save_path = save_uploaded_files(
#                             st.session_state.username,
#                             st.session_state.uploaded_pdfs,
#                             st.session_state.saved_df
#                         )
#                         # if save_path:
#                         #     st.success("✅ Changes saved successfully and files stored!")
                    
#                     # Download section
#                     col1, col2, col3 = st.columns(3)
                    
#                     with col1:
#                         buffer = io.BytesIO()
#                         with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
#                             edited_df.to_excel(writer, index=False)
                        
#                         st.download_button(
#                             label="📥 Download Excel",
#                             data=buffer.getvalue(),
#                             file_name=excel_file,
#                             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#                             key="download_existing"
#                         )
                
#                 except Exception as e:
#                     st.error(f"Error displaying existing table: {str(e)}")
#                     st.error(traceback.format_exc())
#             else:
#                 # Add Extract button to trigger processing
#                 if st.button("🔍 Extract Info from Doctments"):
#                     try:
#                         # Initialize processing
#                         progress_bar = st.progress(0)
#                         status_text = st.empty()
                        
#                         total_files = len(pdfs_to_process)
#                         total_rows_processed = 0
                        
#                         all_data = []
#                         all_headers = None

#                         # Clean up any leftover temporary files
#                         cleanup_temp_files()

#                         # Process each PDF file
#                         for idx, uploaded_pdf_file in enumerate(pdfs_to_process):
#                             tmp_path = None
#                             try:
#                                 status_text.text(f"Processing file {idx + 1} of {total_files}: {uploaded_pdf_file.name}")
                                
#                                 # Create temporary file
#                                 with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
#                                     tmp_file.write(uploaded_pdf_file.getvalue())
#                                     tmp_path = tmp_file.name
                                
#                                 # Process the file
#                                 with st.spinner(f"Extracting text from {uploaded_pdf_file.name}..."):
#                                     pdf_text = extract_text_pdf(tmp_path)
                                
#                                 if pdf_text:
#                                     with st.spinner("Processing extracted text using AKI-GPT..."):
#                                         invoice_info = using_groq(pdf_text)
                                        
#                                         # Process the invoice using process_invoice_lines
#                                         headers, data_rows = process_invoice_lines(
#                                             invoice_info, 
#                                             ""  # Empty string for costing number
#                                         )
                                        
#                                         if headers and data_rows:
#                                             # Set headers if not set yet
#                                             if all_headers is None:
#                                                 all_headers = headers
                                            
#                                             # Add all data rows to our collection
#                                             all_data.extend(data_rows)
                                            
#                                             # Update row count
#                                             total_rows_processed += len(data_rows)
                            
#                             except Exception as e:
#                                 st.error(f"Error processing file {uploaded_pdf_file.name}: {str(e)}")
                            
#                             finally:
#                                 # Clean up temporary file
#                                 if tmp_path and os.path.exists(tmp_path):
#                                     try:
#                                         # Close any open file handles
#                                         gc.collect()
#                                         os.unlink(tmp_path)
#                                     except Exception as cleanup_error:
#                                         st.warning(f"Could not remove temporary file {tmp_path}: {cleanup_error}")
#                                         # Add to a list of files to clean up later
#                                         if 'cleanup_files' not in st.session_state:
#                                             st.session_state.cleanup_files = []
#                                         st.session_state.cleanup_files.append(tmp_path)
                            
#                             progress_bar.progress((idx + 1) / total_files)
#                             gc.collect()
                        
#                         # Update tracking with total files and rows processed
#                         update_user_tracking(
#                             username=st.session_state.username,
#                             files_uploaded=total_files,
#                             rows_processed=total_rows_processed
#                         )
                                                    
#                         if all_data and all_headers:
#                             try:
#                                 # Create DataFrame with all processed data
#                                 df = pd.DataFrame(all_data, columns=all_headers)
#                                 st.session_state.edited_df = df.copy()
                                
#                                 try:
#                                     # Create an editable table
#                                     st.markdown("### 📝 Data Uploaded to System")
                                    
#                                     edited_df = st.data_editor(
#                                         st.session_state.edited_df,
#                                         use_container_width=True,
#                                         num_rows="dynamic",
#                                         column_config={col: st.column_config.Column(
#                                             width="auto",
#                                             help=f"Edit {col}"
#                                         ) for col in st.session_state.edited_df.columns},
#                                         height=600,
#                                         key=f'grid_{datetime.now().strftime("%Y%m%d%H%M%S")}'
#                                     )
                                                            
#                                     # Add search functionality
#                                     search = st.text_input("🔍 Search in table:", key="search_input")
#                                     if search:
#                                         mask = edited_df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
#                                         filtered_df = edited_df[mask]
#                                     else:
#                                         filtered_df = edited_df 
                            
#                                     # Update the session state with edited data
#                                     st.session_state.edited_df = edited_df
#                                     st.markdown(f"**Total Rows:** {len(filtered_df)} | **Total Columns:** {len(filtered_df.columns)}")

#                                     # Save Changes Button
#                                     if st.button("💾 Save Table Changes", key="save_changes"):
#                                         st.session_state.saved_df = edited_df.copy()
#                                         # Save files to storage
#                                         save_path = save_uploaded_files(
#                                             st.session_state.username,
#                                             st.session_state.uploaded_pdfs,
#                                             st.session_state.saved_df
#                                         )
#                                         if save_path:
#                                             st.success("✅ Changes saved successfully and files stored!")
                                            
#                                             # Update tracking
#                                             update_user_tracking(
#                                                 username=st.session_state.username,
#                                                 files_uploaded=len(pdfs_to_process),
#                                                 rows_processed=len(edited_df)
#                                             )
                                    
#                                     # Create download buttons section
#                                     col1, col2, col3 = st.columns(3)
                                    
#                                     # Original data download button
#                                     with col1:
#                                         buffer_original = io.BytesIO()
#                                         with pd.ExcelWriter(buffer_original, engine='openpyxl') as writer:
#                                             df.to_excel(writer, index=False)
#                                         excel_data_original = buffer_original.getvalue()
                                        
#                                         st.download_button(
#                                             label="📥 Download Original Excel",
#                                             data=excel_data_original,
#                                             file_name=f"original_{excel_file}",
#                                             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#                                             key="download_original"
#                                         )
                                    
#                                     # Saved version download button
#                                     with col2:
#                                         if st.session_state.saved_df is not None:
#                                             buffer_saved = io.BytesIO()
#                                             with pd.ExcelWriter(buffer_saved, engine='openpyxl') as writer:
#                                                 st.session_state.saved_df.to_excel(writer, index=False)
#                                             excel_data_saved = buffer_saved.getvalue()
                                            
#                                             st.download_button(
#                                                 label="📥 Download Saved Excel",
#                                                 data=excel_data_saved,
#                                                 file_name=f"saved_{excel_file}",
#                                                 mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#                                                 key="download_saved"
#                                             )
#                                         else:
#                                             st.info("Save your changes first!")
                                    
#                                     # Current state download button
#                                     with col3:
#                                         buffer_current = io.BytesIO()
#                                         with pd.ExcelWriter(buffer_current, engine='openpyxl') as writer:
#                                             edited_df.to_excel(writer, index=False)
                                        
#                                         st.download_button(
#                                             label="📥 Download Current Excel",
#                                             data=buffer_current.getvalue(),
#                                             file_name=f"current_{excel_file}",
#                                             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#                                             key="download_current"
#                                         )
                                    
#                                     # Add download options explanation
#                                     st.markdown("""
#                                     ### 💡 Download Options:
#                                     - **Original Excel**: The data exactly as extracted from PDFs
#                                     - **Saved Excel**: Your last saved changes
#                                     - **Current Excel**: Current state of the table including unsaved changes
#                                     """)
                                    
#                                 except Exception as e:
#                                     st.error(f"Error displaying table and buttons: {str(e)}")
#                                     st.error(traceback.format_exc())
#                             except Exception as e:
#                                 st.error(f"Error creating DataFrame: {str(e)}")
#                                 st.error(traceback.format_exc())
#                         else:
#                             st.error("No valid data could be extracted from the invoices")
                            
#                     except Exception as e:
#                         st.error(f"Error in main processing: {str(e)}")
#                         st.error(traceback.format_exc())      

#             with tab2:
#                 # st.markdown("### 📂 Previous Uploads")
#                 # user_uploads = get_user_uploavds(st.session_state.username)
#                 handle_excel_upload()


#                 # History Tab
#             with tab3:
#                 display_history_tab()

#             if st.session_state.username == 'admin@akigroup.com':
#                 with tab3:
#                     admin_tracking_tab()


def main_app():
    display_branding()
    
    if st.session_state.username == 'admin@akigroup.com':
        tab1, tab2, tab4 = st.tabs(["Upload & Process", "Excel Upload", "User Tracking"])
    else:
        tab1, tab2 = st.tabs(["Upload & Process", " "])
    
    with tab1:
        # st.markdown(f"Welcome to AKI's AI tool to extract data from documents.")

        _, center_col, _ = st.columns([1, 1, 1])
        with center_col:
            if st.button("Process Next Document", key="refresh"):
                refresh_page()
        
        if 'edited_df' not in st.session_state:
            st.session_state.edited_df = None
        if 'saved_df' not in st.session_state:
            st.session_state.saved_df = None
        if 'processing_complete' not in st.session_state:
            st.session_state.processing_complete = False
        if 'uploaded_pdfs' not in st.session_state:
            st.session_state.uploaded_pdfs = []
        if 'grid_key' not in st.session_state:
            st.session_state.grid_key = 'data_editor_1'
        
        uploaded_pdfs = st.file_uploader(
            " ",
            type=["pdf"],
            accept_multiple_files=True,
            # help="You can upload multiple Invoice files for different suppliers",
            key=f"file_uploader_{st.session_state.get('refresh_timestamp', '')}"
        )

        if uploaded_pdfs:
            st.session_state.uploaded_pdfs = uploaded_pdfs

        pdfs_to_process = st.session_state.uploaded_pdfs or uploaded_pdfs

        # st.info("Please use the tool to extract data from PDF documents, For other file type use Excel Upload Tab")


        if pdfs_to_process:
            if st.session_state.edited_df is not None:
                try:
                    # st.markdown("### 📝 Extracted and Edited Data")
                    
                    search_query = st.text_input("Search in table:", key=f"search_input_{st.session_state.grid_key}")
                    
                    display_df = st.session_state.edited_df.copy()
                    
                    if search_query:
                        mask = display_df.astype(str).apply(
                            lambda x: x.str.contains(search_query, case=False)
                        ).any(axis=1)
                        display_df = display_df[mask]
                    
                    edited_df = st.data_editor(
                        display_df,
                        use_container_width=True,
                        num_rows="dynamic",
                        height=600,
                        key=st.session_state.grid_key,
                        column_config={
                            col: st.column_config.Column(
                                width="auto",
                                help=f"Edit {col}"
                            ) for col in display_df.columns
                        }
                    )
                    
                    st.session_state.edited_df = edited_df
                    
                    st.markdown(f"**Total Rows:** {len(edited_df)} | **Total Columns:** {len(edited_df.columns)}")
                    
                    if st.button("💾 Save Table Changes", key="save_changes_existing"):
                        st.session_state.saved_df = edited_df.copy()
                        save_path = save_uploaded_files(
                            st.session_state.username,
                            st.session_state.uploaded_pdfs,
                            st.session_state.saved_df
                        )
                        # if save_path:
                        #     st.success("✅ Changes saved successfully and files stored!")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        buffer = io.BytesIO()
                        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                            edited_df.to_excel(writer, index=False)
                        
                        # st.download_button(
                        #     label="📥 Download Excel",
                        #     data=buffer.getvalue(),
                        #     file_name=excel_file,
                        #     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        #     key="download_existing"
                        # )
                
                except Exception as e:
                    st.error(f"Error displaying existing table: {str(e)}")
                    st.error(traceback.format_exc())
            else:
                if st.button("Extract Info from Documents", key="extractinfofromdocs"):
                    process_uploaded_files(pdfs_to_process)
                # else:
                #     st.info("Please click 'Extract Info from Documents' to process the uploaded PDF files")
    
        # st.markdown("<div style='height: 200px;'></div>", unsafe_allow_html=True)
        
        # excel_file = st.text_input(
        #     "📊 Excel File Name",
        #     value="Data_Extract.xlsx",
        #     help="Enter the name for your output Excel file"
        # )
        
        # if st.button("🚪 Logout", key="logout"):
        #     st.session_state.logged_in = False
        #     st.session_state.username = None
        #     st.rerun()

    with tab2:
        # st.markdown(f"Welcome to AKI's AI Excel Upload tool.")
        
        _, center_col, _ = st.columns([1, 1, 1])
        with center_col:
            if st.button("🔄 Process Next Document", key="refresh_tab2"):
                refresh_page()

                # Spacer to push the bottom section to the bottom
        # st.markdown("<div style='height: 200px;'></div>", unsafe_allow_html=True)
        
                
        handle_excel_upload()
        
        # st.markdown("---")  
        if st.button("🚪 Logout", key="logout_tab2"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()
    
    if st.session_state.username == 'admin@akigroup.com':
        with tab4:
            admin_tracking_tab()


def refresh_page():
    """
    Refresh the page while preserving login session but clearing uploaded files and processed data
    """
    preserved_keys = ['logged_in', 'username']
    
    preserved_values = {}
    for key in preserved_keys:
        if key in st.session_state:
            preserved_values[key] = st.session_state[key]
    
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    for key, value in preserved_values.items():
        st.session_state[key] = value
    
    st.session_state.uploaded_pdfs = []
    st.session_state.edited_df = None
    st.session_state.saved_df = None
    st.session_state.processing_complete = False
    
    st.session_state.refresh_timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")    
    st.rerun()


def main():
    verify_storage_setup()
    setup_storage()
    init_user_tracking()
    
    share_hash = st.query_params.get('share')
    
    if share_hash:
        st.title("🔗 Shared File Viewer")
        check_shared_file()
    else:
        main_app()
        # if not st.session_state.logged_in:
        #     login_page()
        # else:
        #     main_app()
def handle_pdf_error(e, pdf_name):
    """Handle PDF processing errors with appropriate messages and actions"""
    error_msg = str(e).lower()
    
    if "poppler" in error_msg:
        st.error(f"""Error processing {pdf_name}: Poppler is not installed or not found in PATH. 
        Please ensure Poppler is properly installed on the server.""")
    elif "permission" in error_msg:
        st.error(f"Permission error while processing {pdf_name}. Please check file permissions.")
    else:
        st.error(f"Error processing {pdf_name}: {str(e)}")
    
    if st.button("🔄 Retry Processing", key=f"retry_{hash(pdf_name)}"):
        st.session_state.edited_df = None
        st.session_state.saved_df = None
        st.session_state.processing_complete = False
        st.session_state.costing_numbers = {}
        st.rerun()

def display_branding():
    """Display company branding in a consistent, user-friendly way"""
    col1, col2 = st.columns([4,1])
    
    with col1:
        st.markdown("""
        <p style='margin-bottom: 0px; font-size: 1.5rem;'>AKI Agentic AI Intelligent Document Processor</p>
        """, unsafe_allow_html=True)
            
    # with col2:
    #     if os.path.exists("assets/aki.png"):
    #         st.image("assets/aki.png", width=10)  
    #     else:
    #         st.markdown("📁")  
    
    st.markdown("<hr style='margin-top: 0; margin-bottom: 20px;'>", unsafe_allow_html=True)


def process_with_ocr(pdf_path, pdf_name):
    """Process PDF with OCR including error handling and recovery options"""
    """
    try:
        text = extract_text_pdf(pdf_path)
        if not text:
            st.warning(f"No text could be extracted from {pdf_name}. The file might be corrupted or empty.")
            if st.button("🔄 Retry This File", key=f"retry_empty_{hash(pdf_name)}"):
                st.session_state.edited_df = None
                st.rerun()
            return None
        return text
    except Exception as e:
        handle_pdf_error(e, pdf_name)
        return None
    """
    st.info("We are working on it now")
    return None





def process_large_pdf_text(pdf_text, groq_client):
    """
    Process large PDF text by breaking it into chunks of approximately 4K tokens each
    and sequentially sending them to the LLM API.
    
    Args:
        pdf_text (str): The complete text extracted from the PDF
        groq_client: The initialized Groq client
        
    Returns:
        str: The combined result from all chunks
    """
    import re
    
    if not pdf_text:
        return None
    
    estimated_tokens = len(pdf_text) // 4
    
    if estimated_tokens < 6000:
        return using_groq(pdf_text, groq_client)
    
    chunks = []
    current_chunk = ""
    current_token_estimate = 0
    
    paragraphs = re.split(r'\n\s*\n', pdf_text)
    
    for paragraph in paragraphs:
        if not paragraph.strip():
            continue
            
        paragraph_token_estimate = len(paragraph) // 4
        
        if current_token_estimate + paragraph_token_estimate > 4000 and current_chunk:
            chunks.append(current_chunk)
            current_chunk = paragraph
            current_token_estimate = paragraph_token_estimate
        else:
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph
            current_token_estimate += paragraph_token_estimate
    
    if current_chunk:
        chunks.append(current_chunk)
    
    print(f"Split PDF text into {len(chunks)} chunks for processing")
    
    all_results = []
    
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)} with estimated {len(chunk)//4} tokens")
        
        chunk_result = using_groq(chunk, groq_client, is_chunk=(len(chunks) > 1), chunk_num=(i+1), total_chunks=len(chunks))
        
        if chunk_result:
            all_results.append(chunk_result)
    
    if not all_results:
        return None
    
    combined_result = combine_chunked_results(all_results)
    
    return combined_result


def combine_chunked_results(results):
    """
    Intelligently combine results from multiple chunks into a single coherent output.
    
    Args:
        results (list): List of string results from processing each chunk
        
    Returns:
        str: Combined result
    """
    if not results:
        return ""
    
    if len(results) == 1:
        return results[0]
    
    combined_lines = []
    header_line = None
    separator_line = None
    seen_headers = set()
    
    for i, result in enumerate(results):
        if not result or not result.strip():
            continue
            
        lines = result.strip().split('\n')
        
        for j, line in enumerate(lines):
            if not line.strip():
                continue
                
            if '|' in line and line.count('|') > 2 and not header_line:
                header_line = line
                combined_lines.append(line)
                seen_headers.add(line)
                continue
                
            if header_line and set(line.replace('|', '')).issubset({'-', ' '}) and not separator_line:
                separator_line = line
                if line not in combined_lines:
                    combined_lines.append(line)
                continue
            
            if (i > 0 and (line in seen_headers or set(line.replace('|', '')).issubset({'-', ' '}))):
                continue
                
            if "----" not in line:  
                combined_lines.append(line)
    
    return '\n'.join(combined_lines)


def extract_text_pdf_with_chunking(pdf_path, groq_client):
    """
    Extract text from PDF and handle chunking for large files.
    This function handles both machine-readable and scanned PDFs.
    """
    if is_scanned_pdf(pdf_path):
        st.info("We are working on it now")
        return None
    else:
        try:
            with fitz.open(pdf_path) as pdf:
                unique_pages = {}
                for page_num, page in enumerate(pdf):
                    page_text = page.get_text()
                    content_hash = hash(page_text)
                    if content_hash not in unique_pages:
                        unique_pages[content_hash] = page_text
                
                full_text = "\n".join(unique_pages.values())
                
                return process_large_pdf_text(full_text, groq_client)
                
        except Exception as e:
            st.error(f"Error extracting text: {str(e)}")
            return None


def combine_chunked_results(results):
    """
    Intelligently combine results from multiple chunked API calls.
    
    The function identifies table headers, separators, and data rows,
    then combines them while eliminating duplicates.
    
    Args:
        results (list): List of string results from processing each chunk
        
    Returns:
        str: Combined result with consistent table structure
    """
    if not results:
        return ""
    
    if len(results) == 1:
        return results[0]
    
    header_line = None
    separator_line = None
    data_rows = []
    seen_data_rows = set()
    
    for result in results:
        if not result.strip():
            continue
        
        lines = result.strip().split('\n')
        in_table = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if '|' in line and line.count('|') >= 3 and not header_line:
                header_line = line
                in_table = True
                continue
            
            if header_line and '|' in line and set(line.replace('|', '')).issubset({'-', ' '}) and not separator_line:
                separator_line = line
                continue
            
            if '|' not in line or line.count('|') < 3:
                continue
                
            if in_table and line not in seen_data_rows:
                data_rows.append(line)
                seen_data_rows.add(line)
    
    if not header_line:
        return results[0]
    
    combined_lines = [header_line]
    
    if separator_line:
        combined_lines.append(separator_line)
        
    combined_lines.extend(data_rows)
    
    return '\n'.join(combined_lines)


if __name__ == "__main__":
    main()
