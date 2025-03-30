# **Saarthi - AI-Powered Chatbot** 🚀  

Saarthi is an AI-powered chatbot that can detect the language of user input, translate it into English, generate a response using Google's Gemini AI, and then translate the response back into the original language. It features a **Flask-based backend** for processing and a **Streamlit UI** for user interaction.

---

## **📂 Project Structure**
```
Saarthi/
├── README.md
├── chat-app/
│   ├── app.py           # Flask API (Backend)
│   ├── processing.py    # Language Detection, Translation & AI Response
│   ├── ui.py            # Streamlit UI
│   ├── __pycache__/     # Python cache (ignored in .gitignore)
└── requirements.txt     # Project dependencies
```

---

## **⚙️ Features**
✅ **Multilingual Support**: Detects and translates user input automatically.  
✅ **AI-Powered Responses**: Uses Google Gemini AI for generating responses.  
✅ **User-Friendly UI**: Built with Streamlit for a smooth chat experience.  
✅ **REST API**: The backend runs as a Flask API for easy interaction.  
✅ **Modular Code**: Clear separation of UI, API, and processing logic.  

---

## **🛠️ Installation & Setup**
### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/Princccee/Saarthi2.git
cd Saarthi/chat-app
```

### **2️⃣ Create a Virtual Environment**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
```

### **3️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4️⃣ Set Up Environment Variables**
Create a `.env` file in `chat-app/` and add your **Google API Key**:
```
GOOGLE_API_KEY=your_google_api_key_here
```

### **5️⃣ Run the Flask Backend**
```bash
python app.py
```
The API will start at `http://127.0.0.1:5000`.

### **6️⃣ Run the Streamlit UI**
In a new terminal:
```bash
streamlit run ui.py
```
Open the displayed URL in your browser to chat with Saarthi! 🎉

---

## **📺 API Endpoint**
### **POST `/process`**
**Request:**
```json
{
    "text": "नमस्ते, आप कैसे हैं?"
}
```
**Response:**
```json
{
    "response": "मैं ठीक हूं, धन्यवाद!"
}
```

---

## **📝 Usage**
1️⃣ Enter text in **any language** in the chatbox.  
2️⃣ Saarthi will detect the language and **translate** it to English.  
3️⃣ The **AI generates a response** in English.  
4️⃣ The response is **translated back** to the original language.  
5️⃣ You receive the **final response** in the original language!  

---

## **🛠️ Tech Stack**
- **Python 3.11+**
- **Flask** (Backend API)
- **Streamlit** (UI)
- **Deep Translator** (Translation)
- **LangDetect** (Language Detection)
- **Google Gemini AI** (Response Generation)

---

## **🛠️ Future Improvements**
- 🌎 **Support for more translation providers**  
- 🤖 **Voice-to-Text & Text-to-Speech** integration  
- 📊 **Chat history & analytics**  

---

## **🏃‍♂️ Contributing**
We welcome contributions! If you’d like to improve Saarthi:
1. **Fork the repository**  
2. **Create a new branch** (`feature-name`)  
3. **Make your changes & commit**  
4. **Push to your fork & submit a PR**  

---

## **📞 Contact**
📧 **Email**: princceekumar07@example.com  
🔍 **GitHub**: [Princccee](https://github.com/Princccee/Saarthi2.git)  

Let’s make AI chatbots smarter together! 🚀💬

