import streamlit as st
import pyttsx3
import os
import math

st.set_page_config(page_title="Myanmar TTS & SRT", page_icon="🎙️")
st.title("🎙️ Myanmar TTS & SRT Generator")
st.info("👑 ကြော်ငြာပါ၊ အချိန်စောင့်စရာမလိုဘဲ အကန့်အသတ်မရှိ သုံးချင်ပါက VIP ဝယ်ယူရန် နှိပ်ပါ။")

user_text = st.text_area("မြန်မာစာသားများကို ဤနေရာတွင် ရိုက်ထည့်ပါ -", height=200, placeholder="ဒီမှာ မြန်မာစာ ရိုက်ထည့်ပါ...")

# စာလုံးရေနှင့် အချိန် တွက်ချက်ခြင်း
if user_text:
    char_count = len(user_text)
    word_count = len(user_text.split())
    estimated_seconds = math.ceil(char_count * 0.20) 
    st.write(f"📝 စာလုံးရေ: {char_count} | စကားလုံး: {word_count} | ⏱️ ခန့်မှန်းကြာချိန်: {estimated_seconds} စက္ကန့်")

st.subheader("🤖 TTS Engine")
engine_type = st.radio("Engine ရွေးချယ်ပါ -", ["အကိုလေးမြန်မာအသံအုပ်စု (ကျား/မ)", "Gemini API (VIP)"])

# အသံခွဲခြားသတ်မှတ်ခြင်း Dropdown
voice_select = st.selectbox(
    "🎙️ အသံရွေးချယ်ရန် (Voice)", 
    [
        "အကိုလေး (မြန်မာ - ယောက်ျားလေးသံစစ်စစ်)", 
        "အမလေး (မြန်မာ - မိန်းကလေးသံစစ်စစ်)"
    ]
)

file_name = st.text_input("သိမ်းဆည်းမည့် ဖိုင်နာမည် (File Name)", value="Myanmar_TTS")

# SRT (စာတန်းထိုး) ဖန်တီးပေးမည့် Engine
def generate_srt_content(text, total_seconds):
    sentences = [s.strip() for s in text.replace("၊", "။").split("။") if s.strip()]
    if not sentences:
        sentences = [text]
        
    srt_content = ""
    duration_per_sentence = total_seconds / len(sentences)
    current_time = 0.0
    
    for i, sentence in enumerate(sentences):
        start = current_time
        end = current_time + duration_per_sentence
        
        def fmt(secs):
            h = int(secs // 3600)
            m = int((secs % 3600) // 60)
            s = int(secs % 60)
            ms = int((secs % 1) * 1000)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
            
        srt_content += f"{i+1}\n{fmt(start)} --> {fmt(end)}\n{sentence}။\n\n"
        current_time = end
    return srt_content

# Button Click Trigger
if st.button("🚀 Generate Audio & SRT", use_container_width=True):
    if not user_text:
        st.warning("ကျေးဇူးပြု၍ စာသားတစ်ခုခု အရင်ရိုက်ထည့်ပါ။")
    else:
        with st.spinner("အသံဖိုင်နှင့် စာတန်းထိုးများကို ဖန်တီးနေပါသည်..."):
            output_mp3 = f"{file_name}.mp3"
            
            try:
                # Local Engine ကို စတင်နှိုးဆော်ခြင်း
                engine = pyttsx3.init()
                
                # Server ထဲမှာ ရှိသမျှ Voices တွေကို ဆွဲထုတ်ခြင်း
                voices = engine.getProperty('voices')
                
                # ကျား/မ အသံကို ပတ်ဝန်းကျင်အလိုက် ရွေးချယ်ခြင်း
                if "ယောက်ျားလေးသံ" in voice_select:
                    if len(voices) > 0:
                        engine.setProperty('voice', voices[0].id) # ယောက်ျားလေး Voice Base
                else:
                    if len(voices) > 1:
                        engine.setProperty('voice', voices[1].id) # မိန်းကလေး Voice Base
                    elif len(voices) > 0:
                        engine.setProperty('voice', voices[0].id)
                
                # အသံနှုန်းမြှင့်တင်မှုနှုန်း ချိန်ညှိခြင်း (မြန်မာစာအတွက် အသင့်တော်ဆုံးနှုန်း)
                engine.setProperty('rate', 145)
                
                # အသံဖိုင်ကို တိုက်ရိုက်ဆောက်ပြီး Server ထဲတွင် သိမ်းဆည်းခြင်း
                engine.save_to_file(user_text, output_mp3)
                engine.runAndWait()
                
                # ဖိုင်တည်ရှိမှုကို စစ်ဆေးပြီး ဒေတာဖတ်ခြင်း
                if os.path.exists(output_mp3):
                    with open(output_mp3, "rb") as f:
                        audio_bytes = f.read()
                        
                    # SRT ဖိုင် တွက်ချက်ထုတ်ပေးခြင်း
                    srt_data = generate_srt_content(user_text, estimated_seconds)
                    
                    st.success("🎉 အောင်မြင်စွာ ဖန်တီးပြီးပါပြီ။")
                    
                    # UI တွင် အသံနှင့် ဒေါင်းလုဒ်ခလုတ်များ ပြသခြင်း
                    st.subheader("🎵 Output Audio")
                    st.audio(audio_bytes, format="audio/mp3")
                    
                    st.subheader("💾 ဒေါင်းလုဒ်ရယူရန်")
                    
                    st.download_button(
                        label="📥 MP3 Download", 
                        data=audio_bytes, 
                        file_name=output_mp3, 
                        mime="audio/mp3", 
                        use_container_width=True
                    )
                    
                    st.download_button(
                        label="📥 SRT Download", 
                        data=srt_data.encode('utf-8'), 
                        file_name=f"{file_name}.srt", 
                        mime="text/plain", 
                        use_container_width=True
                    )
                    
                    # ယာယီဖိုင်အား ပြန်လည်ရှင်းလင်းခြင်း
                    os.remove(output_mp3)
                else:
                    st.error("အသံဖိုင် ဖန်တီးမှု မအောင်မြင်ပါ။ စာသားပြန်စစ်ပေးပါ။")
                    
            except Exception as e:
                st.error(f"လုပ်ဆောင်မှု အမှန်တကယ် မအောင်မြင်ပါ- {e}")
                    
