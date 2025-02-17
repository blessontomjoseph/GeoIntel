from main import get_map
import streamlit as st

# basic 1-1 no context

# if __name__=="__main__":
#     st.title("NDVI Web App")

#     user_input = st.text_input("Type your message:", "")
#     if user_input:
#         # st.write(f"**You:** {user_input}")
#         map_object = get_map(user_input)
#         map_object.to_streamlit(width=1000,height=500)


# example query like
# Give me the NDVI of trissur for 2020 to 2023.
# show me the ndvi map of kozhikode for last july



# active bot with history

if __name__=="__main__":
    import streamlit as st
    import folium
    from streamlit_folium import st_folium
    
    try:
        if "messages" not in st.session_state:
            st.session_state.messages = []

        st.title("GeoIntel")

        for message in st.session_state.messages:
            with st.chat_message(message["sender"]):
                if message["type"] == "text":
                    st.write(message["text"])
                elif message["type"] == "map":
                    st_folium(message["map"], width=700, height=400)


        user_input = st.chat_input("Type your message...")

        if user_input:
            st.session_state.messages.append({"sender": "user", "text": user_input, "type": "text"})
            
            with st.chat_message("user"):
                st.write(user_input)
            
            bot_map = get_map(user_input)
            st.session_state.messages.append({"sender": "bot", "map": bot_map, "type": "map"})
            
            with st.chat_message("bot"):
                st_folium(bot_map, width=700, height=400)
            
    except:
        with st.chat_message("bot"):
            st.write(user_input)