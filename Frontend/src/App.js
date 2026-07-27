import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import Funding from "./pages/Funding";
import Research from "./pages/Research";
import Profile from "./pages/Profile";
import Login from "./pages/Login";
import ResearchProfile from "./pages/ResearchProfile";
import PublicationTrend from "./pages/PublicationTrend";
import Recommendation from "./pages/Recommendation";
import GrantMatching from "./pages/GrantMatching";
import ResearchDetails from "./pages/ResearchDetails";
import Patents from "./pages/Patents";
import PatentDetails from "./pages/PatentDetails"; 
import AddResearch from "./pages/AddResearch";
import AddPatent from "./pages/AddPatent";
function App() {
  return (
    <BrowserRouter>
    <div style={{display:"flex"}}>
    <Sidebar/>
    <div style={{marginLeft:"250px",width:"100%",padding:"20px"}}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/funding" element={<Funding />} />
        <Route path="/research" element={<Research />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/login" element={<Login />} />
        <Route path="/research-profile" element={<ResearchProfile />} />
        <Route path="/publication-trends" element={<PublicationTrend />} />
        <Route path="/recommendation" element={<Recommendation/>}/>
        <Route path="/grant-matching" element={<GrantMatching />} />
        <Route path="/research" element={<Research />} />
        <Route path="/research-details" element={<ResearchDetails/>}/>
        <Route path="/patents" element={<Patents/>}/>
        <Route path="/patents/:id" element={<PatentDetails/>}/>
      <Route path="/add-research" element={<AddResearch />} />
      <Route path="/add-patent" element={<AddPatent/>}/>
      </Routes>
      </div>
      </div>
      </BrowserRouter>
  );
}
export default App;