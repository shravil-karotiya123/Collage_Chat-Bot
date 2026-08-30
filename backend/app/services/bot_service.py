"""
College Bot Knowledge Base & Response Engine.
"""

from typing import Any, Dict, List

COLLEGE_KNOWLEDGE = {
    "courses": [
        {
            "name": "B.Tech Computer Science & Engineering",
            "duration": "4 Years",
            "eligibility": "10+2 with 60% in PCM + Entrance Qualification",
            "intake": 180,
            "description": "Specializations in AI/ML, Cybersecurity, Cloud Computing, and Data Science.",
        },
        {
            "name": "B.Tech Chemical & Petrochemical Engineering",
            "duration": "4 Years",
            "eligibility": "10+2 with 60% in PCM",
            "intake": 120,
            "description": "Industry-partnered program with focus on refining, process engineering, and energy.",
        },
        {
            "name": "M.Tech Industrial Automation & AI",
            "duration": "2 Years",
            "eligibility": "B.E./B.Tech in relevant branch",
            "intake": 60,
            "description": "Advanced research in robotics, IoT, predictive maintenance, and agentic systems.",
        },
        {
            "name": "MBA Technology Management",
            "duration": "2 Years",
            "eligibility": "Bachelor's Degree with 50% + Entrance Score",
            "intake": 90,
            "description": "Focus on techno-commercial leadership, supply chain, and digital transformation.",
        },
    ],
    "admissions": {
        "status": "Admissions open for 2026-2027 Academic Year",
        "deadline": "July 15, 2026",
        "steps": [
            "Submit online application at campus portal",
            "Upload 10th/12th grade transcripts and entrance scorecard",
            "Participate in online/offline counselling session",
            "Fee payment and document verification",
        ],
        "scholarships": "Merit scholarships up to 100% tuition waiver for top 5% entrance rankers.",
    },
    "placements": {
        "highest_package": "45.0 LPA",
        "average_package": "8.5 LPA",
        "placement_rate": "94.2%",
        "top_recruiters": [
            "MRPL",
            "TATA Consultancy Services",
            "Infosys",
            "Reliance Industries",
            "L&T Technology Services",
            "Microsoft",
            "Bosch",
        ],
    },
    "faqs": [
        {
            "question": "What are the hostel facilities available?",
            "answer": "Separate high-speed Wi-Fi enabled hostels for boys and girls with 24/7 security, gym, and hygienic mess.",
        },
        {
            "question": "Are there research labs and industrial partnerships?",
            "answer": "Yes, we host 5 state-of-the-art research centers partnered with leading industrial enterprises.",
        },
        {
            "question": "How can I apply for financial aid?",
            "answer": "Financial aid forms are available on the admission portal under the 'Scholarships & Aid' section.",
        },
    ],
}


class CollegeBotService:

    def process_query(self, message: str) -> Dict[str, Any]:
        """
        Analyzes incoming student/parent messages and retrieves accurate college responses.
        """
        msg_lower = message.lower().strip()

        # Intent Recognition Rules
        if any(w in msg_lower for w in ["course", "program", "branch", "degree", "btech", "mtech", "mba"]):
            return {
                "reply": "Here are our key academic programs and offerings:",
                "data_type": "courses",
                "data": COLLEGE_KNOWLEDGE["courses"],
                "suggestions": ["Admission Deadline?", "Placement Stats", "Hostel Info"],
            }

        elif any(w in msg_lower for w in ["admission", "apply", "scholarship", "eligibility", "deadline", "fees"]):
            return {
                "reply": f"Admission Status: {COLLEGE_KNOWLEDGE['admissions']['status']}. Application deadline is {COLLEGE_KNOWLEDGE['admissions']['deadline']}.",
                "data_type": "admissions",
                "data": COLLEGE_KNOWLEDGE["admissions"],
                "suggestions": ["Explore Courses", "Placement Package", "Contact Office"],
            }

        elif any(w in msg_lower for w in ["placement", "package", "salary", "recruiter", "company", "jobs"]):
            return {
                "reply": f"Placement Highlights: Highest Package is {COLLEGE_KNOWLEDGE['placements']['highest_package']} with an average package of {COLLEGE_KNOWLEDGE['placements']['average_package']} ({COLLEGE_KNOWLEDGE['placements']['placement_rate']} placed).",
                "data_type": "placements",
                "data": COLLEGE_KNOWLEDGE["placements"],
                "suggestions": ["Top Companies?", "Course List", "Scholarships"],
            }

        elif any(w in msg_lower for w in ["hostel", "facility", "campus", "lab", "faq", "gym", "mess"]):
            return {
                "reply": "Here are answers to frequently asked campus questions:",
                "data_type": "faqs",
                "data": COLLEGE_KNOWLEDGE["faqs"],
                "suggestions": ["Admissions 2026", "Available Courses", "Placement Rate"],
            }

        else:
            return {
                "reply": "Welcome to Campus AI Assistant! I can help you with Course Details, Admission Requirements, Placement Packages, and Campus Facilities. What would you like to explore?",
                "data_type": "general",
                "data": None,
                "suggestions": ["Courses Offered", "Admission Process", "Placement Stats", "Hostel & Facilities"],
            }


bot_service = CollegeBotService()
