import streamlit as st
import wget
from os.path import join
import pandas as pd
import config_example as config
import streamlit.ReportThread as ReportThread
from streamlit.server.Server import Server


def trigger_rerun():
    ctx = ReportThread.get_report_ctx()

    this_session = None

    current_server = Server.get_current()
    if hasattr(current_server, '_session_infos'):
        # Streamlit < 0.56
        session_infos = Server.get_current()._session_infos.values()
    else:
        session_infos = Server.get_current()._session_info_by_id.values()

    for session_info in session_infos:
        s = session_info.session
        if (
                # Streamlit < 0.54.0
                (hasattr(s, '_main_dg') and s._main_dg == ctx.main_dg)
                or
                # Streamlit >= 0.54.0
                (not hasattr(s, '_main_dg') and s.enqueue == ctx.enqueue)
        ):
            this_session = s

    if this_session is None:
        raise RuntimeError(
            "Oh noes. Couldn't get your Streamlit Session object"
            'Are you doing something fancy with threads?')
    this_session.request_rerun()


input_data = pd.read_csv(config.input_data_file, sep='\t', index_col='item_id', error_bad_lines=False)
tagged_data = pd.read_csv(config.tagged_data_file, sep='\t', index_col='item_id')

try:
    item_data = input_data[~input_data.index.isin(tagged_data.index)].iloc[0,:]
    st.image(item_data.url, width=600, caption=item_data.name)
    att_value = st.sidebar.radio(config.attribute_name, config.attribute_values, index=3)
    if st.sidebar.button('Save'):
        item_data.loc['att_value'] = att_value
        item_data[['url', 'att_value']].to_frame().T.to_csv(config.tagged_data_file,
                                                                                          sep='\t', header=False,
                                                                                          index=True,
                                                                                          mode='a')

        wget.download(item_data.url, join(config.image_output_folder,
                                          '{att_value}_{item_id}.jpg'.format(
                                              att_value=item_data.att_value,
                                              item_id=item_data.name)))
        trigger_rerun()
except IndexError:
    st.error("Finished tagging")



