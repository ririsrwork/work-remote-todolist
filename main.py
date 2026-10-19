import streamlit as st
from streamlit_gsheets import GSheetsConnection
from datetime import date
import pandas as pd

st.set_page_config(page_title="Task - To Do List", page_icon="📝", layout="centered")

st.title("📝 Task - To Do List")
st.caption("A task management application powered by Google Sheets & Streamlit")

# Connect to Google Sheets via Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# Function to load data from Google Sheets
def load_data():
    try:
        df = conn.read(worksheet="Sheet1", ttl=0)
        if df.empty or "task" not in df.columns:
            return []
        
        # Clean empty rows
        df = df.dropna(subset=["task"])
        tasks = []
        for _, row in df.iterrows():
            # Convert date strings back to Python date objects
            t_date = date.fromisoformat(str(row["task_date"])) if pd.notna(row["task_date"]) else date.today()
            d_date = date.fromisoformat(str(row["due_date"])) if pd.notna(row["due_date"]) else date.today()
            
            tasks.append({
                "task": str(row["task"]),
                "description": str(row["description"]) if pd.notna(row["description"]) else "",
                "task_date": t_date,
                "due_date": d_date,
                "priority": str(row["priority"]) if pd.notna(row["priority"]) else "Low",
                "status": str(row["status"]) if pd.notna(row["status"]) else "On Progress"
            })
        return tasks
    except Exception as e:
        st.error(f"Failed to load data from Google Sheets: {e}")
        return []

# Function to save data to Google Sheets
def save_data(tasks):
    if tasks:
        df = pd.DataFrame(tasks)
        df["task_date"] = df["task_date"].astype(str)
        df["due_date"] = df["due_date"].astype(str)
    else:
        df = pd.DataFrame(columns=["task", "description", "task_date", "due_date", "priority", "status"])
    
    try:
        # Gunakan pembaruan data yang terjamin menyimpan seluruh dataframe
        conn.update(worksheet="Sheet1", data=df)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Failed to save data to Google Sheets: {e}")
        return False

# Initialize session state
if "tasks" not in st.session_state:
    st.session_state.tasks = load_data()

# Add Task Form
with st.form("add_task_form", clear_on_submit=True):
    new_task = st.text_input("Task Title *", placeholder="E.g., Complete project report...")
    description = st.text_area("Description (Optional)", placeholder="Add details, notes, or links here...")
    
    col_tdate, col_ddate, col_priority, col_status = st.columns(4)
    with col_tdate:
        task_date = st.date_input("Task Date", value=date.today())
    with col_ddate:
        due_date = st.date_input("Due Date", value=date.today())
    with col_priority:
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    with col_status:
        status = st.selectbox("Initial Status", ["On Progress", "FU", "Done"])
    
    submitted = st.form_submit_button("➕ Add Task", use_container_width=True)
    if submitted:
        if new_task.strip() != "":
            st.session_state.tasks.append({
                "task": new_task.strip(),
                "description": description,
                "task_date": task_date,
                "due_date": due_date,
                "priority": priority,
                "status": status
            })
            if save_data(st.session_state.tasks):
                st.success("Task added and saved to Google Sheets successfully!")
                st.rerun()
        else:
            st.warning("Task Title cannot be empty!")

st.divider()

# Task List
if st.session_state.tasks:
    total_count = len(st.session_state.tasks)
    done_count = sum(1 for t in st.session_state.tasks if t["status"] == "Done")
    progress = done_count / total_count if total_count > 0 else 0
    
    st.write(f"**Overall Progress:** {done_count}/{total_count} Done ({int(progress * 100)}%)")
    st.progress(progress)
    
    st.subheader("📋 Your Task List")
    
    for index, item in enumerate(st.session_state.tasks):
        with st.container():
            col_text, col_details, col_action = st.columns([2.5, 2, 1])
            
            with col_text:
                if item["status"] == "Done":
                    st.markdown(f"~~**{item['task']}**~~")
                else:
                    st.markdown(f"**{item['task']}**")
                
                if item.get("description"):
                    st.caption(item["description"])
                
                t_date = item.get("task_date", date.today())
                st.text(f"📌 Task Date: {t_date} | 📅 Due: {item['due_date']}")
            
            with col_details:
                p_color = "🔴" if item["priority"] == "High" else ("🟡" if item["priority"] == "Medium" else "🟢")
                st.caption(f"{p_color} Priority: {item['priority']}")
                
                status_options = ["On Progress", "FU", "Done"]
                current_status_index = status_options.index(item["status"]) if item["status"] in status_options else 0
                
                new_status = st.selectbox(
                    "Status", 
                    status_options, 
                    index=current_status_index, 
                    key=f"status_{index}"
                )
                
                if new_status != item["status"]:
                    st.session_state.tasks[index]["status"] = new_status
                    save_data(st.session_state.tasks)
                    st.rerun()
            
            with col_action:
                st.write("") 
                if st.button("🗑️ Delete", key=f"del_{index}"):
                    st.session_state.tasks.pop(index)
                    save_data(st.session_state.tasks)
                    st.rerun()
                    
            st.divider()
else:
    st.info("No tasks available. Go ahead and add your first task above!")
