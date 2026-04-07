// Chatbot Component
import { useState } from 'react';
import { MessageCircle, Send, X, Bot, Loader } from 'lucide-react';

interface ChatMessage {
  id: string;
  role: 'user' | 'bot';
  content: string;
  timestamp: Date;
}

export function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const quickQuestions = [
    "What products do you offer?",
    "What are your branch hours?",
    "How do I apply for a loan?",
    "What documents do I need?"
  ];

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Simulate API call (replace with actual API)
      const response = await new Promise<string>(resolve => {
        setTimeout(() => {
          resolve(getBotResponse(input));
        }, 1000);
      });

      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'bot',
        content: response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickQuestion = (question: string) => {
    setInput(question);
  };

  const getBotResponse = (message: string): string => {
    const lower = message.toLowerCase();
    
    const responses: Record<string, string> = {
      'hello': 'Hello! Welcome to STBank Laos. How can I help you today?',
      'hi': 'Hi there! How can I assist you?',
      'hours': 'Our branches are open Mon-Fri 8:00-17:00 and Sat 8:00-12:00.',
      'location': 'We have branches in Vientiane, Luang Prab, Pakse, and Savannakhet. Visit stbank.la for addresses.',
      'loan': 'We offer Personal Loans up to 50M LAK and Home Loans up to 500M LAK. Would you like to apply?',
      'savings': 'Our Savings Account offers 4.5% annual interest with no minimum balance!',
      'credit': 'STBank Credit Cards offer great cashback rewards. First year annual fee is free!',
      'contact': 'Call 1629 or visit any STBank branch. Our team is ready to help!',
      'document': 'For loans, you need: ID card, proof of income, and bank statements. Apply in 24 hours!',
      'apply': 'Apply online at lead.stbank.la or visit any branch. Get a call back in 2 hours!',
      'rate': 'Our current rates: Home Loan 7%, Personal Loan 10.5%, Savings 4.5%. Contact for details!',
      'default': 'Thank you! A STBank representative will contact you within 2 hours for more information.'
    };

    for (const [key, response] of Object.entries(responses)) {
      if (lower.includes(key)) {
        return response;
      }
    }

    return responses['default'];
  };

  return (
    <>
      {/* Chat Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-primary-500 rounded-full shadow-lg flex items-center justify-center text-white hover:bg-primary-600 transition-colors z-40"
      >
        <MessageCircle className="w-6 h-6" />
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 w-80 md:w-96 bg-white rounded-xl shadow-xl border border-gray-200 z-40 overflow-hidden">
          {/* Header */}
          <div className="bg-primary-500 text-white px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bot className="w-5 h-5" />
              <span className="font-semibold">STBank Assistant</span>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white hover:bg-primary-600 rounded p-1"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages */}
          <div className="h-80 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-gray-500 py-8">
                <Bot className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p className="text-sm">Hi! How can I help you today?</p>
                <div className="mt-4 space-y-2">
                  {quickQuestions.map((q, i) => (
                    <button
                      key={i}
                      onClick={() => handleQuickQuestion(q)}
                      className="block w-full text-left text-sm px-3 py-2 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors text-gray-700"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map(msg => (
              <div
                key={msg.id}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] px-4 py-2 rounded-lg ${
                    msg.role === 'user'
                      ? 'bg-primary-500 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="text-sm">{msg.content}</p>
                  <p className={`text-xs mt-1 ${
                    msg.role === 'user' ? 'text-primary-200' : 'text-gray-400'
                  }`}>
                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 px-4 py-2 rounded-lg">
                  <Loader className="w-5 h-5 animate-spin text-gray-400" />
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="border-t border-gray-200 p-3">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Type your message..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 text-sm"
                disabled={isLoading}
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                className="w-10 h-10 bg-primary-500 text-white rounded-lg flex items-center justify-center hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default Chatbot;