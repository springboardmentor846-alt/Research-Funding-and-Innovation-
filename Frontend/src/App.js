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
import PatentAnalytics from "./pages/PatentAnalytics";
import TechnologyIntelligence from "./pages/TechnologyIntelligence";
import InnovationScoring from "./pages/InnovationScoring";
import CommercializationRecommendations from "./pages/CommercializationRecommendations";
import InnovationDashboard from "./pages/InnovationDashboard";
import AddTechnology from "./pages/AddTechnology";
import AddInnovation from "./pages/AddInnovation";
import AddCommercialization from "./pages/AddCommercialization";
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
        <Route path="/patent-analytics" element={<PatentAnalytics/>}/>
        <Route path="/technology-intelligence" element={<TechnologyIntelligence/>}/>
        <Route path="/innovation-scoring" element={<InnovationScoring/>}/>
        <Route path="/commercialization-recommendations" element={<CommercializationRecommendations/>}/>
        <Route path="/innovation-dashboard" element={<InnovationDashboard/>}/>
        <Route path="/add-technology" element={<AddTechnology />} />
        <Route path="/add-innovation" element={<AddInnovation />} />
        <Route path="/add-commercialization" element={<AddCommercialization/>}/>
      </Routes>
      </div>
      </div>
      </BrowserRouter>
  );
}
export default App;