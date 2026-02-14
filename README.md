<p align="center">
  <img src="./img.png" alt="Project Banner" width="100%">
</p>
# [Smart Study Planner] 🎯

## Basic Details

### Team Name: [Tiny Coders]

### Team Members
- Member 1: [Jeslin Giby] - [ Jyothi Engineering College,Thrissur]
- Member 2: [Gopika V V] - [Jyothi Engineering College,Thrissur]

### Hosted Project Link
[https://smart-study-planner-1-2.onrender.com/]

### Project Description
[Smart Study Planner is a web-based application that helps students organize their study schedule based on subjects, exam dates, and available study hours.
It automatically distributes study time, generates a daily timetable, and tracks completed topics.
The goal is to improve time management and exam preparation through structured planning and progress monitoring.]

### The Problem statement
[Many students struggle with poor time management and unstructured study plans, especially when preparing for multiple exams with different subjects and deadlines. They often fail to distribute study time effectively, track completed topics, or monitor overall progress. There is a need for a smart system that can organize study schedules, allocate time efficiently, and help students track their preparation in a structured and automated way.]

### The Solution
[The Smart Study Planner solves this problem by providing a web-based platform where students can enter their subjects, exam dates, topics, and available study hours. The system automatically calculates total study time, distributes hours subject-wise based on priority and deadlines, and generates a structured daily timetable.

It also allows students to mark completed topics, track total hours studied, and monitor remaining work, ensuring organized preparation and better time management.]

---

## Technical Details

### Technologies/Components Used

**For Software:**
- Languages used: [e.g., JavaScript, Python(flask),html,css]
- Frameworks used: [e.g.flask(python),HTML 5,CSS3,VANILLA JAVASCRIPT]
- Libraries used: [e.g.Flask- login,flask-cors,JSON module,font awesome]
- Tools used: [e.g., VS Code, Git, Render]


---

## Features

List the key features of your project:
- Feature 1: [Automated Study Schedule Generation]
- Feature 2: [Subject & Exam Management]
- Feature 3: [Progress Tracking System]
- Feature 4: [User Authentication & Data Storage]

---

## Implementation

### For Software:

#### Installation
```bash
[Installation commands - e.g., npm install, pip install -r requirements.txt]
```

#### Run
```bash
[Run commands - e.g., npm start, python app.py]
```


## Project Documentation

### For Software:

#### Screenshots (Add at least 3)

![<img width="1920" height="1020" alt="Screenshot 2026-02-14 074431" src="https://github.com/user-attachments/assets/43ba471c-9db5-4287-bf93-f0e7a6aeb129" />
](Login Page)
Login Page: Secure user login and registration interface for accessing personalized study plans.

![<img width="1920" height="1020" alt="Screenshot 2026-02-14 074710" src="https://github.com/user-attachments/assets/e65474cb-7995-4721-9ace-ecc6766d1017" />
](Dashboard Overview)
Dashboard Overview: Main dashboard to add subjects, set exam dates, and view daily schedule with study statistics.
![<img width="1920" height="1020" alt="Screenshot 2026-02-14 074723" src="https://github.com/user-attachments/assets/4182bb2f-4740-4354-ba1f-6e54db5c0b3d" />
](Progress Tracking Page)
Progress Tracking Page: Section to update study hours, mark completed topics, and monitor overall learning progress.
#### Diagrams

**System Architecture:**

![Architecture Diagram](![system architecture](https://github.com/user-attachments/assets/d1e17392-d01e-4a6b-b47b-a36039d24f0c)
)
The Smart Study Planner is designed using a three-tier architecture that separates the system into Presentation, Application, and Database layers to ensure better organization, scalability, and maintainability.

The Presentation Layer (Frontend) is developed using HTML, CSS, and JavaScript. This layer is responsible for handling all user interactions, such as logging in, adding subjects, entering exam dates, and updating study progress. It collects user input and sends requests to the backend through HTTP routes.

**Application Workflow:**

![Workflow](![WhatsApp Image 2026-02-14 at 8 58 16 AM](https://github.com/user-attachments/assets/b057264b-2736-4419-9249-cd5b3c069ff1)
)
The Smart Study Planner workflow begins when a user registers or logs into the system. After authentication, the user adds subjects, exam dates, topics, and total study hours. The frontend sends this data to the Flask backend through HTTP routes. The backend processes the information, calculates study schedules, distributes hours, and stores data in the SQLite database. Users can then update daily progress by logging hours studied and marking completed topics. The system retrieves updated data from the database and dynamically displays schedules, statistics, and remaining tasks on the dashboard for continuous tracking and improvement.
---


## Additional Documentation

### For Web Projects with Backend:

#### API Documentation

**Base URL:** `https://api.yourproject.com`

##### Endpoints

**GET /**
- **Description:** returns the index.html file, which contains the functionalities of signin/register
- **Response:**
```
index.html
```

**GET /home**
- **Description:** Shows the home page of the Smart study planner after the user successfully logins.
- **Response:**
```file
home.html
```

**GET /dashboard**
- **Description:** The dashboard itself will enforce auth via API calls (401 -> redirect on frontend).
- **Response:**
```file
dashboard.html
```

**POST /api/register**
- **Description:** Register authentication-related API routes on the given Flask app.
- **Request Body:**
```json
{
  "username": "name",
  "email": "eg@gmail.com",
  "password":"pass"
}
```
- **Response:**
```json
{"message": "Registration successful"}
```

**POST /api/login**
- **Description:** allows users to Login to the app.
- **Request Body:**
```json
{
  "username": "name",
  "password":"pass"
}
```
- **Response:**
```json
 {"message": "Login successful", "user": {"id": user.id, "username": user.username}}
```


**POST /api/logout**
- **Description:** Allows users to Logout
- **Response:**
```json
 {"message": "Logged out"}
```

**POST /api/chatgpt**
- **Description:** Register chatbot-related API routes.
- **Request:**
```json
 {"user_message": "who are you"}
```
- **Response:**
```json
 {"reply": "hi iam the all knowing model"}
```

**POST /api/progress**
- **Description:** Register chatbot-related API routes.
- **Request:**
```json
 {
  "subject_id": "",
  "hours_studied":"",
  "topics_completed";"",
  "date_str":"",
 }
```
- **Response:**
```json
{"message": "Progress updated"}
```


**GET /api/daily-schedule**
- **Description:** Returns the daily schedule of the user.
- **Response:**
```json
{
  "subject_id": subj.id,
  "name": subj.name,
  "exam_date": subj.exam_date.isoformat(),
  "hours_per_day": hours_per_day,
  "priority": priority,
}
```

**GET /api/week-view**
- **Description:** Returns the week view of the schedule.
- **Response:**
```json
{
  "date": current_day.isoformat(),
  "subjects": day_schedule,
  "total_hours": ""                
}
## GET /api/stats
- **Description:** Returns overall study statistics for the logged-in user.
- **Response:**
```json
{
  "stats": {
    "total_hours_studied": 0,
    "total_topics_completed": 0,
    "total_topics_remaining": 0,
    "subjects_count": 0
  }
}
```

---

## GET /api/history
- **Description:** Returns the last 30 days of study history, including daily totals and total hours per subject.
- **Response:**
```json
{
  "daily_totals": [
    {
      "date": "2026-02-14",
      "hours": 2.5
    }
  ],
  "by_subject": [
    {
      "subject_id": 1,
      "name": "Mathematics",
      "total_hours": 10.5
    }
  ]
}
```

---

## GET /api/settings
- **Description:** Returns the current user settings.
- **Response:**
```json
{
  "settings": {
    "max_daily_hours": 6,
    "show_dashboard_tour": true
  }
}
```

---

## PUT /api/settings
- **Description:** Updates user settings such as maximum daily study hours and dashboard tour visibility.
- **Request Body:**
```json
{
  "max_daily_hours": 6,
  "show_dashboard_tour": true
}
```
- **Response:**
```json
{
  "settings": {
    "max_daily_hours": 6,
    "show_dashboard_tour": true
  }
}
```

## GET /api/subjects
- **Description:** Returns all subjects for the logged-in user, including progress statistics and suggested daily study hours.
- **Response:**
```json
{
  "subjects": [
    {
      "id": 1,
      "name": "Mathematics",
      "exam_date": "2026-03-15",
      "total_hours_needed": 40,
      "topics": ["Algebra", "Calculus", "Geometry"],
      "progress": {
        "total_hours_studied": 10,
        "topics_completed": 2,
        "topics_remaining": 1,
        "completion_percentage": 25
      },
      "hours_per_day": 2.0
    }
  ]
}
```

---

## POST /api/subjects
- **Description:** Creates a new subject for the logged-in user.
- **Request Body:**
```json
{
  "name": "Mathematics",
  "exam_date": "2026-03-15",
  "total_hours_needed": 40,
  "topics": ["Algebra", "Calculus", "Geometry"]
}
```
- **Validation Rules:**
  - `name`, `exam_date`, and `total_hours_needed` are required.
  - `exam_date` must be in ISO format (`YYYY-MM-DD`).
  - `total_hours_needed` must be a positive number.
  - `topics` must be a list.
- **Success Response (201 Created):**
```json
{
  "subject": {
    "id": 1,
    "name": "Mathematics",
    "exam_date": "2026-03-15",
    "total_hours_needed": 40,
    "topics": ["Algebra", "Calculus", "Geometry"],
    "hours_per_day": 2.0
  }
}
```
- **Error Response (400 Bad Request):**
```json
{
  "error": "Error message describing the validation issue"
}
```





[Add more endpoints as needed...]

---

### For Scripts/CLI Tools:

#### Command Reference

**Basic Usage:**
```bash
python script.py [options] [arguments]
```


#### Demo Output
https://drive.google.com/file/d/1G_koIAd79k1qydcl66tZZxuL9-hDsb8B/view?usp=sharing
**Input:**
```
This is a sample input file
with multiple lines of text
for demonstration purposes
```

**Command:**
```bash
python script.py sample.txt
```

**Output:**
```
Processing: sample.txt
Lines processed: 3
Characters counted: 86
Status: Success
Output saved to: output.txt
```


## Project Demo
https://smart-study-planner-1-2.onrender.com/
### Video
[https://drive.google.com/file/d/1G_koIAd79k1qydcl66tZZxuL9-hDsb8B/view?usp=sharing]

The Smart Study Planner workflow begins when a user registers or logs into the system. After authentication, the user adds subjects, exam dates, topics, and total study hours. The frontend sends this data to the Flask backend through HTTP routes. The backend processes the information, calculates study schedules, distributes hours, and stores data in the SQLite database. Users can then update daily progress by logging hours studied and marking completed topics. The system retrieves updated data from the database and dynamically displays schedules, statistics, and remaining tasks on the dashboard for continuous tracking and improvement.

## AI Tools Used (Optional - For Transparency Bonus)

If you used AI tools during development, document them here for transparency:

**Tool Used:** [GitHub Copilot, Cursor, ChatGPT]

**Purpose:** [What you used it for]
 "To get the error in the code"
 "Debugging assistance for async functions"
 "Code review and optimization suggestions"

**Key Prompts Used:**
- "Create a REST API endpoint for user authentication"
- "Debug this async function that's causing race conditions"
- "Optimize this database query for better performance"

**Percentage of AI-generated code:** [Approximately 75%]

**Human Contributions:**
- Architecture design and planning
- Integration and testing
- UI/UX design decisions
- Idea Generation
- Rectify errors
- Base code

## Team Contributions

- [Jeslin Giby]: [Specific contributions -  Frontend development, API integration, etc.]
- [Gopika V V]: [Specific contributions - Backend development, Database design, etc.]



## License

This project is licensed under the [LICENSE_NAME] License - see the [LICENSE](LICENSE) file for details.

**Common License Options:**
- MIT License (Permissive, widely used)
- Apache 2.0 (Permissive with patent grant)
- GPL v3 (Copyleft, requires derivative works to be open source)

---

Made with ❤️ at TinkerHub
