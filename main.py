import streamlit as st
from datetime import date

st.set_page_config(page_title="Task - To Do List", page_icon="📝", layout="centered")

st.title("📝 Task - To Do List")
st.caption("A task management application powered by Python & Streamlit")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

# Add Task Form
with st.form("add_task_form", clear_on_submit=True):
    new_task = st.text_input("Task Title *", placeholder="E.g., Complete project report...")
    description = st.text_area("Description (Optional)", placeholder="Add details, notes, or links here...")
    
    # 4 Columns in form: Task Date, Due Date, Priority, Status
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
    if submitted and new_task.strip() != "":
        st.session_state.tasks.append({
            "task": new_task,
            "description": description,
            "task_date": task_date,
            "due_date": due_date,
            "priority": priority,
            "status": status
        })
        st.success("Task added successfully!")
        st.rerun()

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
                
                # Display Task Date & Due Date
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
                    st.rerun()
            
            with col_action:
                st.write("") 
                if st.button("🗑️ Delete", key=f"del_{index}"):
                    st.session_state.tasks.pop(index)
                    st.rerun()
                    
            st.divider()
else:
    st.info("No tasks available. Go ahead and add your first task above!")
