export default function TypingIndicator() {
  return (
    <div className="flex space-x-2 p-2">
      <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce [animation-delay:-0.3s]"></div>
      <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce [animation-delay:-0.15s]"></div>
      <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce"></div>
    </div>
  );
}
