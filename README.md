
# 🐝 NUEVO-HIVE-DASHBOARD

**NUEVO-HIVE-DASHBOARD** is a web dashboard that helps vending operators track **daily sales**, **slot activity**, and **inventory status** in a clear, visual format.  
It is designed for both **Drink** and **Snack** vending machines, turning raw CSV sales data into **interactive charts** and **slot-level analytics**.

---

## 🚀 Overview

This app simplifies vending management by combining your **daily CSV sales exports** into a unified dashboard.  
You’ll be able to **log in**, **upload sales data**, and **instantly visualize**:

- Daily and total revenue  
- Slot-level sales performance  
- Empty or inactive slots (based on no activity over time)  
- Long-term sales trends (weekly/monthly overview)

The goal is to give a **clean, visual snapshot** of vending operations, making restocking and performance tracking effortless.

---

## 🔐 1. Login & Authentication

- **Login Page**: Secure login form (email + password)  
- **User Roles**:
  - **Admin**: Manage users, upload data, configure slots  

---

## 📦 2. Drag-and-Drop Upload System

- Upload one or multiple **Sales Activity CSV** files (like the ones you exported).  
- The system parses key columns:
  - `Date` → transaction timestamp  
  - `Amount` → revenue per sale  
  - `Details` → **encodes slot ID + price**, e.g. `0B04($2.50)`  
  - `Tran #` → unique transaction  
- Files are validated and combined internally into the database.  
- Duplicate transactions are skipped (detected via Tran # + Device).

### 💡 Example: Slot Detection Logic
Since the file doesn’t explicitly list snack names, each slot is identified from the **Details** field (`0B04`, `0E01`, etc.).  
We’ll map those IDs into a **Slot Table**, and future updates may allow custom product names or capacity tracking.

---

## 🧠 3. Data Processing Plan

After upload, the app will automatically:
1. Parse and normalize all rows.  
2. Compute **daily totals** by slot and device.  
3. Track **last sale date** for each slot.  
4. Estimate **empty slots** using these heuristics:
   - If a slot **has no sales for 2–3 days**, it’s **likely empty**.  
   - If restock counts are provided (e.g., slot has 10 snacks, but only 5 were loaded), countdown sales from that total until zero.  
   - Combine both methods for reliability.

Future versions can add **alerts** (email or dashboard notifications) when a slot is inactive beyond a threshold.

---

## 📊 4. Dashboard Views

| View | Description |
|------|--------------|
| **Overview** | Shows total daily revenue, number of transactions, and activity across all machines. |
| **Device View** | Lists devices with per-slot sales and color-coded indicators (green = active, red = empty). |
| **Slot Detail** | Displays recent sales timeline for each slot and “last sold” timestamp. |
| **Over-Time** | Weekly or monthly trend graphs using line charts or heatmaps. |

Interactive graphs (using tools like Recharts or Chart.js) will make trends easy to see at a glance.

---

## 🧩 5. Architecture Plan
Anything is fine.
---

## 🧱 6. Database (Conceptual)

**Transactions Table**
| Column | Description |
|---------|--------------|
| `tran_no` | Transaction ID |
| `device` | Machine ID |
| `location` | Machine location |
| `slot_id` | Parsed from `Details` |
| `amount` | Sale price |
| `timestamp` | From Date column |
| `details_raw` | Original Details string |

**Slots Table**
| Column | Description |
|---------|--------------|
| `slot_id` | e.g., 0B04 |
| `location` | Machine location |
| `capacity` | Default count (e.g., 10) |
| `current_count` | Tracked automatically |
| `last_sold_date` | Last recorded transaction |

---

## 🔍 7. Empty Slot Logic (v1 Heuristic)

1. If no sale for a slot in **2–3 days**, mark it as “Inactive.”  
2. Combine that with restock history when available:
   - Start from count (e.g., 6)
   - Decrement with each sale
   - Once count reaches 0 → mark as “Empty”

---


## 🗂️ 10. Usage Flow

1. Login to dashboard  
2. Drag-and-drop your daily CSV file  
3. Data auto-processes and refreshes charts  
4. View slot activity, total revenue, and empty-slot warnings  

---

## 📅 11. MVP Milestones

| Phase | Goals |
|--------|--------|
| **v0.1** | Login, Upload, Parse CSV, Store Data |
| **v0.2** | Display Daily Revenue Chart |
| **v0.3** | Slot Tracker + Empty Slot Heuristic |
| **v0.4** | Over-Time Trends |
| **v1.0** | Full Admin + Multi-User Support |
