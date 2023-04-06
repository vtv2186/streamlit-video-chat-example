from streamlit_server_state import server_state, server_state_lock
from streamlit_webrtc import ClientSettings, WebRtcMode, webrtc_streamer
import av

def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")

    flipped = img[::-1,:,:]

    return av.VideoFrame.from_ndarray(flipped, format="bgr24")


def main():
    if "webrtc_contexts" not in server_state:
        server_state["webrtc_contexts"] = []

    self_ctx = webrtc_streamer(
        key="self",
        mode=WebRtcMode.SENDRECV,
        video_frame_callback=video_frame_callback,
        client_settings=ClientSettings(
            rtc_configuration={  # Add this line
      # "iceServers": [{"urls": ["stun:stun4.l.google.com:19302"]}]
     #  "iceServers": [{   "urls": [ "stun:ws-turn1.xirsys.com" ]}, {   "username": "_gOvGuKm6kPUXW7I78axfsf8e7hlY2VaJziOfzYjFnnEZqUb50vvQhQQzevloqKTAAAAAGQc1ox2aXNobnV0ZWph",   "credential": "6b2aa7c4-c9cc-11ed-b509-0242ac140004",   "urls": [       "turn:ws-turn1.xirsys.com:80?transport=udp",       "turn:ws-turn1.xirsys.com:3478?transport=udp",       "turn:ws-turn1.xirsys.com:80?transport=tcp",       "turn:ws-turn1.xirsys.com:3478?transport=tcp",       "turns:ws-turn1.xirsys.com:443?transport=tcp",       "turns:ws-turn1.xirsys.com:5349?transport=tcp"   ]}]
  
    },
            media_stream_constraints={"video": True, "audio": True},
        ),
        sendback_audio=False,
    )

    with server_state_lock["webrtc_contexts"]:
        webrtc_contexts = server_state["webrtc_contexts"]
        if self_ctx.state.playing and self_ctx not in webrtc_contexts:
            webrtc_contexts.append(self_ctx)
            server_state["webrtc_contexts"] = webrtc_contexts
        elif not self_ctx.state.playing and self_ctx in webrtc_contexts:
            webrtc_contexts.remove(self_ctx)
            server_state["webrtc_contexts"] = webrtc_contexts

    active_other_ctxs = [
        ctx for ctx in webrtc_contexts if ctx != self_ctx and ctx.state.playing
    ]

    for ctx in active_other_ctxs:
        webrtc_streamer(
            key=str(id(ctx)),
            mode=WebRtcMode.RECVONLY,
            client_settings=ClientSettings(
                rtc_configuration={  # Add this line
          # "iceServers": [{"urls": ["stun:stun4.l.google.com:19302"]}]
        #   "iceServers": [{   "urls": [ "stun:ws-turn1.xirsys.com" ]}, {   "username": "_gOvGuKm6kPUXW7I78axfsf8e7hlY2VaJziOfzYjFnnEZqUb50vvQhQQzevloqKTAAAAAGQc1ox2aXNobnV0ZWph",   "credential": "6b2aa7c4-c9cc-11ed-b509-0242ac140004",   "urls": [       "turn:ws-turn1.xirsys.com:80?transport=udp",       "turn:ws-turn1.xirsys.com:3478?transport=udp",       "turn:ws-turn1.xirsys.com:80?transport=tcp",       "turn:ws-turn1.xirsys.com:3478?transport=tcp",       "turns:ws-turn1.xirsys.com:443?transport=tcp",       "turns:ws-turn1.xirsys.com:5349?transport=tcp"   ]}]
       "iceServers": [{
          "urls": [ "stun:ws-turn4.xirsys.com" ]
       }, {
          "username": "UIvu1OpNVH8Aw_IWuAYaSU2o6WaTD2hyykLgfqkO563ivxUWWAfnguGDIar3AaoaAAAAAGQrHyp2aXNobnV0ZWph",
          "credential": "eebe884a-d24f-11ed-9d96-0242ac140004",
          "urls": [
              "turn:ws-turn4.xirsys.com:80?transport=udp",
              "turn:ws-turn4.xirsys.com:3478?transport=udp",
              "turn:ws-turn4.xirsys.com:80?transport=tcp",
              "turn:ws-turn4.xirsys.com:3478?transport=tcp",
              "turns:ws-turn4.xirsys.com:443?transport=tcp",
              "turns:ws-turn4.xirsys.com:5349?transport=tcp"
          ]
       }]
        },
                media_stream_constraints={
                    "video": True,
                    "audio": True,
                },
            ),
            source_audio_track=ctx.output_audio_track,
            source_video_track=ctx.output_video_track,
            desired_playing_state=ctx.state.playing,
        )


if __name__ == "__main__":
    main()
