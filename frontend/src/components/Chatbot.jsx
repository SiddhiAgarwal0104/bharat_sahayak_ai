import { useState, useRef, useEffect } from "react"
import { MessageSquare, X, Send, Loader2 } from "lucide-react"
import { sendChatMessage } from "../api/api"

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([
    {
      role: "bot",
      text: "Namaste! I am the Bharat Sahayak AI Assistant. How can I help you navigate our schemes today?"
    }
  ])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const endOfMessagesRef = useRef(null)

  useEffect(() => {
    if (endOfMessagesRef.current) {
      endOfMessagesRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages])

  const handleSend = async (e) => {
    if (e) e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput("")
    setMessages(prev => [...prev, { role: "user", text: userMessage }])
    setLoading(true)

    try {
      const { data } = await sendChatMessage(userMessage)
      setMessages(prev => [...prev, { role: "bot", text: data.reply }])
    } catch (err) {
      console.error(err)
      setMessages(prev => [...prev, { role: "bot", text: "Sorry, I am facing some issues connecting to the server right now." }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 p-4 bg-green-600 text-white rounded-full shadow-xl hover:bg-green-700 hover:scale-105 transition-all z-50 flex items-center justify-center group"
        aria-label={isOpen ? "Close Chatbot" : "Open Chatbot"}
      >
        {isOpen ? <X size={24} /> : <MessageSquare size={24} />}
        {!isOpen && (
          <span className="absolute right-full mr-3 bg-white text-neutral-800 text-sm py-1 px-3 rounded-xl shadow-md opacity-0 group-hover:opacity-100 whitespace-nowrap transition-opacity pointer-events-none">
            Have a question?
          </span>
        )}
      </button>

      {/* Chatbot Window */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 w-[340px] h-[500px] bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden z-40 border border-neutral-200">
          
          {/* Header */}
          <div className="bg-green-600 text-white p-4 flex justify-between items-center shrink-0">
            <h3 className="font-bold flex items-center gap-2">
              <MessageSquare size={18} /> Sahayak Guide
            </h3>
            <button onClick={() => setIsOpen(false)} className="hover:bg-white/20 p-1 rounded-full transition-colors">
              <X size={20} />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-neutral-50/50">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`p-3 max-w-[85%] rounded-2xl ${
                  msg.role === "user" 
                    ? "bg-green-600 text-white rounded-br-sm" 
                    : "bg-white text-neutral-800 border border-neutral-100 shadow-sm rounded-bl-sm"
                }`}>
                  <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.text}</p>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="p-3 max-w-[85%] bg-white text-neutral-800 border border-neutral-100 shadow-sm rounded-2xl rounded-bl-sm flex items-center gap-2">
                  <Loader2 className="animate-spin text-green-600" size={16} />
                  <span className="text-sm text-neutral-500">Typing...</span>
                </div>
              </div>
            )}
            <div ref={endOfMessagesRef} />
          </div>

          {/* Input Area */}
          <div className="p-3 bg-white border-t border-neutral-100 shrink-0">
            <form onSubmit={handleSend} className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask me anything..."
                className="flex-1 bg-neutral-100 border-transparent focus:border-green-600 focus:ring-1 focus:ring-green-600 rounded-xl px-4 py-2 text-sm outline-none transition-all"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={!input.trim() || loading}
                className="bg-green-600 text-white hover:bg-green-700 p-2 w-10 h-10 rounded-xl flex items-center justify-center disabled:opacity-50 transition-all shrink-0"
              >
                <Send size={18} />
              </button>
            </form>
          </div>
          
        </div>
      )}
    </>
  )
}