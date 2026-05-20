import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from reportlab.platypus import SimpleDocTemplate, Table
from io import BytesIO
import streamlit as st

st.set_page_config(
    page_title="AcademiaX",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>

/* Works in BOTH themes */
.stApp {
    background-color: transparent;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111827;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Metrics - adaptive */
[data-testid="metric-container"] {
    background-color: rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 15px;
}

/* Buttons */
.stButton > button {
    background-color: #2563EB;
    color: white !important;
}

/* Text safety */
h1, h2, h3, p, label {
    color: inherit !important;
}

</style>
""", unsafe_allow_html=True)
st.title("🎓 AcademiaX")
st.subheader("Academic Management System")

conn = sqlite3.connect("academiax.db")

cursor = conn.cursor()

menu = st.sidebar.selectbox(

"Menu",

[
"Dashboard",
"Add Student",
"View Students",
"Add Subject",
"Delete Subject",
"View Subjects",
"Add Marks",
"View Marks",
"Update Student",
"Delete Student",
"Search Student",
"Reports",
]

)


if menu == "Dashboard":

    st.title("🎓 AcademiaX Dashboard")
    st.caption(
        "Academic Management & Analytics System"
    )

    # -------------------
    # Metrics
    # -------------------

    total_students = pd.read_sql_query(
        "SELECT COUNT(*) count FROM students",
        conn
    )

    total_subjects = pd.read_sql_query(
        "SELECT COUNT(*) count FROM subjects",
        conn
    )

    avg_marks = pd.read_sql_query(
        "SELECT AVG(marks) avg FROM marks",
        conn
    )

    top_student = pd.read_sql_query(
        """

        SELECT students.name,

        AVG(marks.marks)

        avg_marks

        FROM marks

        JOIN students

        ON marks.student_id =
        students.student_id

        GROUP BY students.name

        ORDER BY avg_marks DESC

        LIMIT 1

        """,

        conn
    )


    c1,c2,c3,c4 = st.columns(4)


    with c1:

        st.metric(

            "👨‍🎓 Students",

            int(
            total_students["count"][0]
            )

        )


    with c2:

        st.metric(

            "📚 Subjects",

            int(
            total_subjects["count"][0]
            )

        )


    with c3:

        avg = avg_marks["avg"][0]

        st.metric(

            "📈 Avg Marks",

            round(avg,1)

            if avg else 0

        )


    with c4:

        if not top_student.empty:

            st.metric(

            "🏆 Top",

            top_student["name"][0]

            )


    st.divider()


    # -------------------
    # Charts
    # -------------------

    left,right = st.columns(2)


    with left:

        st.subheader(
            "📊 Subject Performance"
        )

        query = """

        SELECT

        subjects.subject_name,

        AVG(marks.marks)

        avg_marks

        FROM marks

        JOIN subjects

        ON marks.subject_id =
        subjects.subject_id

        GROUP BY subjects.subject_name

        """

        chart = pd.read_sql_query(
            query,
            conn
        )


        if not chart.empty:

            fig = px.bar(

                chart,

                x="subject_name",

                y="avg_marks",

                color="avg_marks"

            )

            st.plotly_chart(
                fig,

                use_container_width=True
            )



    with right:

        st.subheader(
            "🥇 Student Ranking"
        )

        rank = pd.read_sql_query(

        """

        SELECT

        students.name,

        AVG(marks.marks)

        avg_marks

        FROM marks

        JOIN students

        ON marks.student_id =
        students.student_id

        GROUP BY students.name

        ORDER BY avg_marks DESC

        """,

        conn

        )

        st.dataframe(
            rank,

            use_container_width=True
        )


    st.divider()


    # -------------------
    # Recent Students
    # -------------------

    st.subheader(
        "🆕 Recent Students"
    )

    recent = pd.read_sql_query(

    """

    SELECT *

    FROM students

    ORDER BY student_id DESC

    LIMIT 5

    """,

    conn

    )

    st.dataframe(

        recent,

        use_container_width=True

    )


    st.success(
    "🎯 AcademiaX System Running"
    )

# ADD STUDENT
elif menu=="Add Student":

    st.header("Add Student")

    name = st.text_input("Student Name")

    usn = st.text_input("USN")

    sem = st.number_input(

    "Semester",

    1,

    8

    )

    dept = st.text_input(

    "Department"

    )


    if st.button("Save"):

        cursor.execute(

        """

        INSERT INTO students(

        name,

        usn,

        semester,

        department

        )

        VALUES(?,?,?,?)

        """,

        (name,usn,sem,dept)

        )

        conn.commit()

        st.success("Saved")


# VIEW STUDENTS
elif menu=="View Students":

    data = pd.read_sql_query(

    "SELECT * FROM students",

    conn

    )

    st.dataframe(data)

# ADD SUBJECT
elif menu=="Add Subject":

    st.header("Add Subject")

    subject = st.text_input(
        "Subject Name"
    )

    credits = st.number_input(
        "Credits",
        1,
        10
    )

    semester = st.number_input(
        "Semester",
        1,
        8
    )


    if st.button("Save Subject"):

        cursor.execute(

        """

        INSERT INTO subjects(

        subject_name,

        credits,

        semester

        )

        VALUES(?,?,?)

        """,

        (subject,credits,semester)

        )

        conn.commit()

        st.success(
        "Subject Added"
        )



# VIEW SUBJECTS
elif menu=="View Subjects":

    data = pd.read_sql_query(

    "SELECT * FROM subjects",

    conn

    )

    st.dataframe(data)
# ADD MARKS
elif menu == "Add Marks":

    st.header("Add Marks")

    # Load students
    students = pd.read_sql_query(
        "SELECT student_id, name FROM students",
        conn
    )

    # Load subjects
    subjects = pd.read_sql_query(
        "SELECT subject_id, subject_name FROM subjects",
        conn
    )


    if students.empty or subjects.empty:

        st.warning(
            "Add students and subjects first."
        )

    else:

        student = st.selectbox(

            "Select Student",

            students["name"]

        )


        subject = st.selectbox(

            "Select Subject",

            subjects["subject_name"]

        )


        marks = st.number_input(
            "Marks",
            0,
            100
        )


        # Auto grade
        if marks >= 90:
            grade = "A+"
        elif marks >= 80:
            grade = "A"
        elif marks >= 70:
            grade = "B"
        elif marks >= 60:
            grade = "C"
        else:
            grade = "F"


        st.write("Grade:", grade)


        if st.button("Save Marks"):

            student_id = int(

                students[
                    students["name"] == student
                ]["student_id"].iloc[0]

            )


            subject_id = int(

                subjects[
                    subjects["subject_name"] == subject
                ]["subject_id"].iloc[0]

            )


            cursor.execute(

                """

                INSERT INTO marks(

                student_id,

                subject_id,

                marks,

                grade

                )

                VALUES(?,?,?,?)

                """,

                (

                student_id,

                subject_id,

                marks,

                grade

                )

            )


            conn.commit()

            st.success(
                "Marks Added"
            )



# VIEW MARKS
elif menu == "View Marks":

    st.title("📑 Student Results")

    query = """

    SELECT

    students.name,

    students.usn,

    subjects.subject_name,

    marks.marks,

    marks.grade

    FROM marks

    JOIN students

    ON marks.student_id =
    students.student_id

    JOIN subjects

    ON marks.subject_id =
    subjects.subject_id

    """

    data = pd.read_sql_query(
        query,
        conn
    )


    if data.empty:

        st.warning(
            "No marks available"
        )

    else:

        search = st.text_input(
            "🔍 Search Student"
        )

        filtered = data[

        data["name"]

        .str.contains(

        search,

        case=False,

        na=False

        )

        ]


        st.dataframe(

        filtered,

        use_container_width=True

        )


        st.divider()


        st.subheader(
        "🏆 Top Scorers"
        )


        top = filtered.sort_values(

        by="marks",

        ascending=False

        ).head(5)


        st.dataframe(
        top,
        use_container_width=True
        )


        st.divider()


        st.subheader(
        "📊 Marks Distribution"
        )

        import plotly.express as px

        fig = px.bar(

            filtered,

            x="name",

            y="marks",

            color="subject_name",

            barmode="group",

            title="Student Performance"

        )


        st.plotly_chart(

        fig,

        use_container_width=True

        )


        csv = filtered.to_csv(
        index=False
        )


        st.download_button(

        "⬇ Download Results",

        csv,

        "results.csv",

        "text/csv"

        )  
# UPDATE STUDENT
elif menu == "Update Student":

    st.header("Update Student")

    sid = st.number_input(
        "Student ID",
        1
    )

    new_name = st.text_input(
        "New Name"
    )

    new_sem = st.number_input(
        "New Semester",
        1,
        8
    )

    new_dept = st.text_input(
        "New Department"
    )


    if st.button(
        "Update"
    ):

        cursor.execute(

        """

        UPDATE students

        SET

        name=?,

        semester=?,

        department=?

        WHERE

        student_id=?

        """,

        (

        new_name,

        new_sem,

        new_dept,

        sid

        )

        )

        conn.commit()

        st.success(
        "Student Updated"
        )    
# DELETE STUDENT
elif menu == "Delete Student":

    st.header("Delete Student")

    sid = st.number_input(
        "Student ID to delete",
        1
    )

    if st.button(
        "Delete"
    ):

        cursor.execute(

        """

        DELETE FROM students

        WHERE student_id=?

        """,

        (sid,)

        )

        conn.commit()

        st.success(
        "Student Deleted"
        )
# SEARCH STUDENT
elif menu=="Search Student":

    st.header(
        "Search Student"
    )

    name = st.text_input(
        "Enter Name"
    )

    query = f"""

    SELECT *

    FROM students

    WHERE name

    LIKE '%{name}%'

    """

    data = pd.read_sql_query(
        query,
        conn
    )

    st.dataframe(data)  
# REPORTS
elif menu == "Reports":

    st.header("📊 Academic Reports")

    query = """

    SELECT

    students.name,

    AVG(marks.marks)

    as average_marks

    FROM marks

    JOIN students

    ON marks.student_id =
    students.student_id

    GROUP BY students.name

    """

    data = pd.read_sql_query(
        query,
        conn
    )


    if data.empty:

        st.warning(
            "No reports available"
        )

    else:

        st.dataframe(
            data,
            use_container_width=True
        )


        top = data.loc[
            data["average_marks"].idxmax()
        ]


        st.success(

        f"🏆 Top Performer: "

        f"{top['name']} "

        f"({round(top['average_marks'],1)})"

        )


        # CSV DOWNLOAD
        csv = data.to_csv(
            index=False
        )


        st.download_button(

            "⬇ Download CSV",

            csv,

            file_name=
            "report.csv",

            mime=
            "text/csv"

        )


        # PDF DOWNLOAD
        pdf_buffer = BytesIO()

        doc = SimpleDocTemplate(
            pdf_buffer
        )

        table_data = [

            data.columns.tolist()

        ] + data.values.tolist()


        table = Table(
            table_data
        )

        doc.build([table])

        pdf = pdf_buffer.getvalue()


        st.download_button(

            label=
            "📄 Download PDF",

            data=
            pdf,

            file_name=
            "AcademiaX_Report.pdf",

            mime=
            "application/pdf"

        )    
# DELETE SUBJECT
elif menu == "Delete Subject":

    st.header("🗑️ Delete Subject")

    # show subjects for reference
    subjects = pd.read_sql_query(
        "SELECT subject_id, subject_name FROM subjects",
        conn
    )

    st.dataframe(subjects)

    sid = st.number_input(
        "Enter Subject ID to delete",
        1
    )

    if st.button("Delete Subject"):

        cursor.execute("""

            DELETE FROM subjects
            WHERE subject_id=?

        """, (sid,))

        conn.commit()

        st.success("Subject Deleted Successfully")                 
conn.close()