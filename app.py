import streamlit as st
import settings

# --------------------------------------------------------------------------------

# Initialize Session State variables:
if 'message' not in st.session_state:
    st.session_state.message = 'To use this application, please login...'
if 'token' not in st.session_state:
    st.session_state.token = {'value': None, 'expiry': None}
if 'user' not in st.session_state:
    st.session_state.user = None
if 'email' not in st.session_state:
    st.session_state.email = None
if 'report' not in st.session_state:
    st.session_state.report = []

# --------------------------------------------------------------------------------

import streamlit_debug

streamlit_debug.set(flag=False, wait_for_client=True, host='localhost', port=6789)

# --------------------------------------------------------------------------------

from common import messageboard, check_token
import dumb_app, dumber_app

# --------------------------------------------------------------------------------

# !! Appears to throw errors if initialized using messageboard.empty() !!
messageboard = st.empty()


# --------------------------------------------------------------------------------

def main():
    if settings.USE_AUTHENTICATION:
        AUTH_LABEL = 'Authenticate'

        label = AUTH_LABEL
        if (check_token(st.session_state.token)):
            label = f'{st.session_state.user} ({st.session_state.email})'

        with st.expander(label, expanded=True):
            import component_runner
            from component_event_handler import handle_event

            component_runner.init(handle_event)

            # force a rerun to flip the expander label
            just_logged_in = bool(check_token(st.session_state.token) and label == AUTH_LABEL)
            just_logged_out = bool(not check_token(st.session_state.token) and label != AUTH_LABEL)
            if (just_logged_in or just_logged_out):
                st.experimental_rerun()

    pages = {
        'DuMMMy aPp 1': [dumb_app.main],  # DUMMY APP 1
        'DUmmmY ApP 2': [dumber_app.main],  # DUMMY APP 2
    }

    def _launch_apps():
        messageboard.empty()
        choice = st.sidebar.radio('What do you want to do?', tuple(pages.keys()))
        pages[choice][0](title=choice, *pages[choice][1:])

    if settings.USE_AUTHENTICATION:
        if (check_token(st.session_state.token)):
            _launch_apps()
        else:
            messageboard.info('Please login below...')
    else:
        _launch_apps()

    st.markdown('---')

    if st.checkbox('Show debug info', False):
        st.write('Token:', st.session_state.token)
        st.write('User:', st.session_state.user)
        st.write('Email:', st.session_state.email)

    # ABOUT
    st.sidebar.title('Component Auth0 Demo')
    st.sidebar.info('Streamlit application integrating Auth0 user indentity and API access authentication.\n\n' + \
                    '(c) 2022. CloudOpti Ltd. All rights reserved.')
    st.sidebar.markdown('---')


def hide_streamlit_styles():
    hide_streamlit_styles = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_styles, unsafe_allow_html=True)


def add_custom_footer():
    auth0_svg = """
        <svg width="54" height="16" viewBox="0 0 81 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18.5334 0H10.7619L13.1617 7.51092H20.9333L14.6477 11.984L17.0475 19.5348C21.0922 16.5767 22.4192 12.0956 20.9333 7.50295L18.5334 0ZM0.590492 7.51092H8.36206L10.7619 0H2.9903L0.590492 7.51092C-0.895483 12.1036 0.431564 16.5846 4.47628 19.5428L6.87609 11.992L0.590492 7.51092ZM4.47628 19.5348L10.7619 23.9999L17.0475 19.5348L10.7619 14.99L4.47628 19.5348ZM63.1286 7.31956C61.293 7.31956 60.1169 8.15677 59.5686 9.52022H59.4256V3.34085H56.6682V19.5029H59.4891V12.4863C59.4891 10.7481 60.5619 9.75145 62.0797 9.75145C63.5577 9.75145 64.4318 10.7003 64.4318 12.3189V19.5029H67.2527V11.8484C67.2448 8.93816 65.6078 7.31956 63.1286 7.31956ZM74.8733 3.30895C71.0591 3.30895 68.7546 6.30694 68.7467 11.5136C68.7467 16.7361 71.0352 19.774 74.8733 19.774C78.7035 19.782 81 16.7441 81 11.5136C80.9921 6.31492 78.6876 3.30895 74.8733 3.30895ZM71.663 11.5136C71.6709 7.71026 72.9026 5.70894 74.8733 5.70894C76.2242 5.70894 77.2255 6.63385 77.7261 8.42786L71.7107 12.8132C71.6789 12.4146 71.663 11.976 71.663 11.5136ZM74.8733 17.3421C73.4827 17.3421 72.4576 16.3534 71.9729 14.4398L78.0201 10.0305C78.0678 10.493 78.0916 10.9873 78.0916 11.5215C78.0916 15.3488 76.8599 17.3421 74.8733 17.3421ZM43.9698 14.4557C43.9698 16.2816 42.6666 17.1906 41.419 17.1906C40.0602 17.1906 39.1623 16.2258 39.1623 14.7029V7.49498H36.3413V15.1415C36.3413 18.0278 37.9783 19.6624 40.3304 19.6624C42.1263 19.6624 43.3818 18.7135 43.9301 17.374H44.0572V19.5109H46.7908V7.49498H43.9698V14.4557ZM29.9603 7.31159C27.4413 7.31159 25.5104 8.43584 24.8906 10.6285L27.5208 11.0033C27.7989 10.182 28.5936 9.48035 29.9762 9.48035C31.2874 9.48035 32.0026 10.1501 32.0026 11.3302V11.378C32.0026 12.1913 31.1523 12.2312 29.0386 12.4544C26.7182 12.7016 24.4932 13.4033 24.4932 16.1062C24.4932 18.4664 26.2176 19.7182 28.4982 19.7182C30.3736 19.7182 31.494 18.8331 32.0105 17.8285H32.1059V19.479H34.8156V11.4418C34.8235 8.2684 32.2489 7.31159 29.9603 7.31159ZM32.0105 15.1654C32.0105 16.5049 30.9378 17.6371 29.2372 17.6371C28.0612 17.6371 27.2188 17.0949 27.2188 16.0584C27.2188 14.974 28.1645 14.5195 29.42 14.3361C30.159 14.2325 31.637 14.0491 32.0105 13.7461V15.1654ZM52.8142 4.48901H49.9932V7.49498H48.2847V9.75145H49.9932V16.4012C49.9773 18.6577 51.6143 19.774 53.7359 19.7102C54.3717 19.6943 54.8484 19.5906 55.1742 19.4949V17.2544C54.9597 17.2863 54.4591 17.3501 54.1015 17.3581C53.3942 17.374 52.8221 17.1109 52.8221 15.9627V9.75145H55.1742V7.50295H52.8142V4.48901Z" fill="#000"></path>
        </svg>
    """
    footer = """
    <style>
        a:link, a:visited {
            color: LightBlue;
            background-color: transparent;
            text-decoration: underline;
        }
        a:hover, a:active {
            color: LightRed;
            background-color: transparent;
            text-decoration: underline;
        }
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: transparent;
            color: grey;
            text-align: center;
        }
        .footer > p {
            font-size: 14px;
        }
    </style>
    <div class="footer">
        <p>
        Developed for <a href="https://auth0.com/">@SVG@</a>
        by <a style='display: inline-block;' href="https://www.linkedin.com/in/asehmi/" target="_blank">Arvindra Sehmi</a> with ❤️
        | <a style='display: block-inline; text-align: center;' href="https://github.com/asehmi" target="_blank">Github</a>
        </p>
    </div>
    """.replace('@SVG@', auth0_svg)
    st.markdown(footer, unsafe_allow_html=True)


if __name__ == '__main__':
    hide_streamlit_styles()

    st.sidebar.image('./images/logo.png', output_format='png')
    main()

    add_custom_footer()