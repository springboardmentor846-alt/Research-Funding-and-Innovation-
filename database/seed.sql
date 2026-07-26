-- Test user (password: test1234)
INSERT INTO users (name, email, password, role) VALUES
('Test Researcher', 'test@test.com', '$2b$12$KIX9r3e1234567890abcdefuZQJ1234567890abcdefghijklmnopq', 'researcher')
ON CONFLICT (email) DO NOTHING;

-- Funding Opportunities
INSERT INTO funding_opportunities_v2 (title, agency, funding_amount, deadline, country, research_domain, eligibility, description, application_link, status) VALUES
('AI Research Innovation Grant', 'National Science Foundation', 500000, '2025-09-30', 'USA', 'Artificial Intelligence', 'Open to universities and research institutions with active AI programs', 'Funding for cutting-edge AI research including machine learning, NLP, and computer vision projects.', 'https://nsf.gov/apply', 'Open'),
('Climate Change & Sustainability Fund', 'European Research Council', 750000, '2025-08-15', 'EU', 'Environmental Science', 'Open to EU-based research institutions and universities', 'Supporting research on climate change mitigation, renewable energy, and sustainable development.', 'https://erc.europa.eu/apply', 'Open'),
('Biomedical Research Excellence Award', 'NIH', 1200000, '2025-10-01', 'USA', 'Biomedical', 'Open to accredited medical schools and biomedical research centers', 'Advancing biomedical research in genomics, drug discovery, and personalized medicine.', 'https://nih.gov/grants', 'Open'),
('Quantum Computing Research Initiative', 'DARPA', 2000000, '2025-07-31', 'USA', 'Quantum Computing', 'Open to universities and national laboratories with quantum research facilities', 'Accelerating quantum computing hardware and algorithm development for national security applications.', 'https://darpa.mil/apply', 'Open'),
('Global Health Innovation Fund', 'WHO', 300000, '2025-11-30', 'Global', 'Public Health', 'Open to NGOs, universities, and health research institutions worldwide', 'Supporting innovative solutions to global health challenges including infectious diseases and healthcare access.', 'https://who.int/grants', 'Open'),
('Cybersecurity Research Program', 'DHS', 450000, '2025-08-31', 'USA', 'Cybersecurity', 'Open to US-based universities and research labs', 'Research on advanced cybersecurity threats, zero-trust architecture, and critical infrastructure protection.', 'https://dhs.gov/research', 'Open'),
('Renewable Energy Technology Grant', 'Department of Energy', 900000, '2025-12-15', 'USA', 'Energy', 'Open to universities, national labs, and private research institutions', 'Developing next-generation solar, wind, and energy storage technologies.', 'https://energy.gov/grants', 'Open'),
('Data Science & Analytics Fellowship', 'Gates Foundation', 250000, '2025-09-15', 'Global', 'Data Science', 'Open to researchers from developing countries and global institutions', 'Applying data science to solve humanitarian challenges in education, health, and poverty.', 'https://gatesfoundation.org/apply', 'Open'),
('Robotics & Automation Research Fund', 'IEEE Foundation', 350000, '2025-10-31', 'Global', 'Robotics', 'Open to universities and research institutions with robotics programs', 'Advancing robotics research in autonomous systems, human-robot interaction, and industrial automation.', 'https://ieee.org/grants', 'Open'),
('Neuroscience Discovery Grant', 'Brain Research Foundation', 600000, '2025-11-15', 'USA', 'Neuroscience', 'Open to accredited neuroscience research centers and universities', 'Exploring brain function, neurological disorders, and cognitive science breakthroughs.', 'https://brainresearch.org/grants', 'Open'),
('Space Technology Research Award', 'NASA', 1500000, '2025-07-15', 'USA', 'Aerospace', 'Open to universities and aerospace research institutions', 'Research on space exploration technologies, satellite systems, and deep space missions.', 'https://nasa.gov/grants', 'Open'),
('Agricultural Innovation Fund', 'USDA', 400000, '2025-10-15', 'USA', 'Agriculture', 'Open to agricultural universities and research stations', 'Developing sustainable farming technologies, crop resilience, and food security solutions.', 'https://usda.gov/grants', 'Open');

-- Publications
INSERT INTO publications_v2 (title, year, authors, citation_count, research_domain, keywords, organization) VALUES
('Deep Learning for Medical Image Analysis', 2023, 'Ahmed K., Smith J., Lee M.', 145, 'Artificial Intelligence', 'deep learning, medical imaging, CNN, diagnosis', 'MIT'),
('Climate Modeling with Neural Networks', 2022, 'Johnson R., Patel S.', 89, 'Environmental Science', 'climate change, neural networks, prediction, modeling', 'Stanford University'),
('CRISPR Gene Editing Advances', 2023, 'Williams T., Brown A., Davis C.', 210, 'Biomedical', 'CRISPR, gene editing, genomics, therapy', 'Harvard Medical School'),
('Quantum Entanglement in Computing', 2021, 'Chen X., Kumar V.', 178, 'Quantum Computing', 'quantum computing, entanglement, qubits, algorithms', 'Caltech'),
('COVID-19 Vaccine Efficacy Study', 2022, 'Martinez L., Thompson K.', 320, 'Public Health', 'vaccine, COVID-19, efficacy, immunology', 'Johns Hopkins'),
('Zero-Trust Security Architecture', 2023, 'Anderson P., White S.', 67, 'Cybersecurity', 'cybersecurity, zero-trust, network security, authentication', 'Carnegie Mellon'),
('Perovskite Solar Cell Efficiency', 2022, 'Taylor R., Jackson M.', 134, 'Energy', 'solar energy, perovskite, efficiency, renewable', 'NREL'),
('Predictive Analytics in Healthcare', 2023, 'Harris N., Clark B.', 98, 'Data Science', 'data science, healthcare, predictive analytics, machine learning', 'University of Michigan'),
('Autonomous Robot Navigation', 2021, 'Lewis D., Robinson E.', 156, 'Robotics', 'robotics, autonomous navigation, SLAM, sensors', 'Georgia Tech'),
('Alzheimer Early Detection via MRI', 2022, 'Walker F., Hall G.', 201, 'Neuroscience', 'neuroscience, Alzheimer, MRI, early detection', 'Mayo Clinic'),
('Mars Terrain Analysis Using AI', 2023, 'Young H., King I.', 88, 'Aerospace', 'space, Mars, AI, terrain analysis, NASA', 'JPL'),
('Drought-Resistant Crop Engineering', 2021, 'Scott J., Green K.', 112, 'Agriculture', 'agriculture, drought resistance, crop engineering, GMO', 'Iowa State University'),
('Transformer Models for NLP', 2022, 'Adams L., Baker M.', 445, 'Artificial Intelligence', 'NLP, transformers, BERT, language models', 'Google Research'),
('Ocean Acidification Impact Study', 2021, 'Carter N., Mitchell O.', 76, 'Environmental Science', 'ocean, acidification, climate, marine biology', 'Woods Hole'),
('mRNA Therapeutics Development', 2023, 'Perez P., Roberts Q.', 189, 'Biomedical', 'mRNA, therapeutics, drug delivery, vaccines', 'Moderna Research'),
('Quantum Error Correction Methods', 2022, 'Turner R., Phillips S.', 143, 'Quantum Computing', 'quantum, error correction, fault tolerance, qubits', 'IBM Research'),
('Malaria Prevention in Sub-Saharan Africa', 2021, 'Campbell T., Parker U.', 95, 'Public Health', 'malaria, prevention, Africa, public health', 'WHO Research'),
('AI-Powered Intrusion Detection', 2023, 'Evans V., Edwards W.', 72, 'Cybersecurity', 'AI, intrusion detection, cybersecurity, anomaly detection', 'MIT Lincoln Lab'),
('Wind Turbine Optimization', 2022, 'Collins X., Stewart Y.', 108, 'Energy', 'wind energy, turbine, optimization, renewable', 'NREL'),
('Big Data in Financial Markets', 2021, 'Morris Z., Rogers A.', 167, 'Data Science', 'big data, finance, analytics, machine learning', 'Wharton School');
