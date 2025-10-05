import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import NodeView from "./pages/NodeView";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/nodes" element={<NodeView />} />
    </Routes>
  );
}

export default App;
