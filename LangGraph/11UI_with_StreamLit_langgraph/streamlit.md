# UI Building with Streamlit — Detailed Guide

Since you're learning **ML and Data Science**, Streamlit is especially useful because it lets you turn a Python/ML model into an interactive web application **without needing to build a separate frontend with React, HTML, CSS, and JavaScript**.

The key idea is:

> **Python code → Streamlit components → Interactive browser UI → ML model**

Streamlit apps are Python scripts that execute from top to bottom, and when a user interacts with a widget, Streamlit reruns the script and redraws the UI. ([Streamlit Docs][1])

---

# 1. What is Streamlit?

Streamlit is a Python framework for building data and ML applications.

For example, instead of building:

```text
React frontend
      ↓
REST API
      ↓
Flask/FastAPI backend
      ↓
ML model
```

you can build:

```text
Streamlit
    ↓
Python code
    ↓
ML model
```

A simple ML application could look like:

```text
┌──────────────────────────────────────────────┐
│              House Price Predictor           │
├──────────────────────────────────────────────┤
│                                              │
│  Area:       [ 1500          ]               │
│  Bedrooms:   [ 3             ]               │
│  Bathrooms:  [ 2             ]               │
│  Location:   [ Kathmandu ▼   ]               │
│                                              │
│              [ Predict Price ]               │
│                                              │
│  Predicted Price:                            │
│  Rs. 12,500,000                               │
│                                              │
└──────────────────────────────────────────────┘
```

---

# 2. Installing Streamlit

Inside your virtual environment:

```bash
pip install streamlit
```

Verify:

```bash
streamlit --version
```

Create:

```text
app.py
```

Then:

```bash
streamlit run app.py
```

Streamlit starts a local development server and opens the application in your browser.

---

# 3. Your First Streamlit UI

```python
import streamlit as st

st.title("My First Streamlit App")

st.write("Hello World!")

st.header("Machine Learning")

st.text("This is a Streamlit application.")
```

The important thing to understand is that **you don't manually create HTML elements**.

Instead of:

```html
<h1>My First Streamlit App</h1>
```

you write:

```python
st.title("My First Streamlit App")
```

---

# 4. Understanding the Streamlit Execution Model

This is probably the **most important Streamlit concept**.

Suppose you have:

```python
import streamlit as st

st.title("Counter")

count = 0

if st.button("Increment"):
    count += 1

st.write(count)
```

You might expect:

```text
Click
 ↓
count becomes 1

Click again
 ↓
count becomes 2
```

But you will keep getting:

```text
1
```

Why?

Because Streamlit reruns the entire script whenever you interact with a widget. ([Streamlit Docs][2])

Conceptually:

```text
User clicks button
        ↓
Streamlit reruns app.py
        ↓
count = 0
        ↓
button returns True
        ↓
count += 1
        ↓
count = 1
```

On the next click:

```text
User clicks
      ↓
app.py reruns
      ↓
count = 0 again
      ↓
count += 1
      ↓
1
```

This is why **Session State** is important.

---

# 5. Session State

Use:

```python
st.session_state
```

to preserve information between reruns.

Example:

```python
import streamlit as st

if "count" not in st.session_state:
    st.session_state.count = 0

st.title("Counter")

if st.button("Increment"):
    st.session_state.count += 1

st.write("Count:", st.session_state.count)
```

Now:

```text
Initial
Count: 0

Click
Count: 1

Click
Count: 2

Click
Count: 3
```

Session State is associated with an individual browser session and can preserve values across reruns and pages. ([Streamlit Docs][2])

---

# 6. Text Components

Streamlit provides many components for displaying information.

### Title

```python
st.title("House Price Prediction")
```

### Header

```python
st.header("Input Features")
```

### Subheader

```python
st.subheader("Model Prediction")
```

### Markdown

```python
st.markdown("## Machine Learning Model")
```

### Text

```python
st.text("Simple text")
```

### Write

```python
st.write("Hello")
```

`st.write()` is particularly useful because it can display different Python objects.

```python
name = "Suman"
age = 22

st.write(name)
st.write(age)
```

You can also:

```python
st.write({
    "name": "Suman",
    "age": 22
})
```

---

# 7. Displaying DataFrames

For ML projects, this is extremely useful.

```python
import streamlit as st
import pandas as pd

df = pd.DataFrame({
    "Name": ["Ram", "Hari", "Sita"],
    "Age": [20, 22, 21]
})

st.dataframe(df)
```

You get an interactive table.

You can also use:

```python
st.table(df)
```

Difference:

```text
st.dataframe()
    ↓
Interactive dataframe

st.table()
    ↓
Static table
```

For ML applications, `st.dataframe()` is generally more useful.

---

# 8. Input Widgets

This is where Streamlit becomes useful for ML applications.

---

## 8.1 Text Input

```python
name = st.text_input("Enter your name")

st.write("Hello", name)
```

---

## 8.2 Number Input

```python
age = st.number_input(
    "Enter your age",
    min_value=0,
    max_value=100,
    value=20
)

st.write(age)
```

Very useful for:

```text
Age
Salary
Income
House area
Temperature
Number of bedrooms
etc.
```

---

# 9. Slider

```python
age = st.slider(
    "Age",
    min_value=0,
    max_value=100,
    value=25
)

st.write("Selected age:", age)
```

For ML:

```python
temperature = st.slider(
    "Temperature",
    -20.0,
    50.0,
    25.0
)
```

---

# 10. Selectbox

```python
city = st.selectbox(
    "Select city",
    ["Kathmandu", "Pokhara", "Lalitpur", "Bhaktapur"]
)

st.write(city)
```

This is useful for categorical ML features.

For example:

```python
education = st.selectbox(
    "Education",
    ["High School", "Bachelor", "Master", "PhD"]
)
```

---

# 11. Radio Buttons

```python
gender = st.radio(
    "Gender",
    ["Male", "Female", "Other"]
)
```

---

# 12. Checkbox

```python
smoker = st.checkbox("Smoker")

if smoker:
    st.write("Smoker selected")
```

Useful for binary features:

```text
Yes / No
True / False
0 / 1
```

---

# 13. Multiselect

```python
skills = st.multiselect(
    "Select your skills",
    ["Python", "C++", "JavaScript", "ML", "Deep Learning"]
)

st.write(skills)
```

Returns something like:

```python
["Python", "ML", "Deep Learning"]
```

---

# 14. File Upload

Extremely important for ML/DS applications.

```python
uploaded_file = st.file_uploader(
    "Upload CSV",
    type=["csv"]
)

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.dataframe(df)
```

Now you have a simple:

```text
CSV
 ↓
Upload
 ↓
Pandas
 ↓
DataFrame
 ↓
Streamlit
```

application.

---

# 15. Image Upload

Useful for computer vision.

```python
uploaded_image = st.file_uploader(
    "Upload an image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_image:
    st.image(uploaded_image)
```

You can then pass that image to a CNN.

---

# 16. Buttons

```python
if st.button("Predict"):
    st.write("Prediction started...")
```

This is commonly used to trigger ML inference.

For example:

```python
if st.button("Predict Price"):
    prediction = model.predict(X)

    st.success(f"Predicted price: {prediction[0]}")
```

---

# 17. Forms

Suppose you have 10 ML inputs.

Without a form:

```text
Input 1 → rerun
Input 2 → rerun
Input 3 → rerun
Input 4 → rerun
...
```

You may want the user to fill everything first and then submit once.

Use:

```python
with st.form("prediction_form"):

    age = st.number_input("Age")
    salary = st.number_input("Salary")
    experience = st.number_input("Experience")

    submitted = st.form_submit_button("Predict")

if submitted:
    st.write("Running prediction...")
```

Forms are useful because they group inputs and let you submit them together rather than triggering the app's normal rerun behavior for each input. ([Streamlit Docs][3])

---

# 18. Columns

This is one of the most important UI layout features.

```python
col1, col2 = st.columns(2)

with col1:
    st.number_input("Age")

with col2:
    st.number_input("Salary")
```

Instead of:

```text
Age

Salary
```

you get:

```text
┌───────────────┐ ┌───────────────┐
│ Age           │ │ Salary        │
└───────────────┘ └───────────────┘
```

Streamlit's layout system supports columns, containers, tabs, expanders, popovers and other mechanisms for organizing UI. ([Streamlit Docs][4])

---

# 19. Three Columns

```python
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Accuracy", "94%")

with col2:
    st.metric("Precision", "91%")

with col3:
    st.metric("Recall", "89%")
```

This is excellent for ML dashboards.

---

# 20. Metric Cards

```python
st.metric(
    label="Model Accuracy",
    value="94.5%",
    delta="+2.3%"
)
```

You can create:

```text
┌─────────────┐
│ Accuracy    │
│ 94.5%       │
│ ↑ +2.3%     │
└─────────────┘
```

---

# 21. Sidebar

The sidebar is ideal for filters and controls that should remain available while viewing the main content.

```python
st.sidebar.title("Settings")

model_type = st.sidebar.selectbox(
    "Model",
    ["Random Forest", "Logistic Regression", "SVM"]
)

threshold = st.sidebar.slider(
    "Threshold",
    0.0,
    1.0,
    0.5
)
```

The official layout guidance recommends `st.sidebar` for persistent controls. ([Streamlit Docs][4])

---

# 22. Tabs

Tabs are useful when you want several logical sections without creating separate pages.

```python
tab1, tab2, tab3 = st.tabs([
    "Prediction",
    "Data",
    "Model"
])

with tab1:
    st.header("Prediction")

with tab2:
    st.header("Dataset")

with tab3:
    st.header("Model Information")
```

Conceptually:

```text
┌────────────┬──────────┬──────────────┐
│ Prediction │   Data   │ Model        │
└────────────┴──────────┴──────────────┘
```

---

# 23. Expander

Useful for hiding advanced information.

```python
with st.expander("View model details"):

    st.write("Algorithm: Random Forest")
    st.write("Trees: 200")
    st.write("Max depth: 10")
```

---

# 24. Containers

Containers allow you to group UI elements.

```python
with st.container():

    st.subheader("Prediction Results")

    st.write("Model prediction:")
    st.metric("Price", "Rs. 12,500,000")
```

You can also create placeholders:

```python
placeholder = st.empty()

placeholder.write("Loading...")

# later
placeholder.success("Prediction completed!")
```

---

# 25. Alerts

Streamlit provides several useful message components.

### Success

```python
st.success("Prediction completed successfully!")
```

### Error

```python
st.error("Invalid input!")
```

### Warning

```python
st.warning("Model confidence is low.")
```

### Information

```python
st.info("Upload a CSV file to continue.")
```

### Exception

```python
st.exception(e)
```

---

# 26. Progress Bar

Useful for long-running ML processes.

```python
progress = st.progress(0)

for i in range(100):
    progress.progress(i + 1)
```

You can use this for:

```text
Data preprocessing
       ↓
Feature engineering
       ↓
Model inference
       ↓
Prediction
```

---

# 27. Spinners

For expensive operations:

```python
with st.spinner("Loading model..."):
    model = load_model()
```

The UI tells the user that something is happening instead of appearing frozen.

---

# 28. Charts

Streamlit supports several chart types.

For example:

```python
import pandas as pd
import streamlit as st

df = pd.DataFrame({
    "sales": [100, 150, 120, 200, 250]
})

st.line_chart(df)
```

You can also use libraries such as:

```text
Matplotlib
Seaborn
Plotly
Altair
```

For example:

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()

ax.plot(
    [1, 2, 3, 4],
    [10, 20, 15, 30]
)

st.pyplot(fig)
```

---

# 29. ML Example — Iris Classifier

Now let's combine the concepts.

Suppose you have an Iris classification model.

```python
import streamlit as st
import numpy as np
import joblib

model = joblib.load("iris_model.pkl")

st.title("🌸 Iris Flower Classifier")

st.sidebar.header("Flower Features")

sepal_length = st.sidebar.slider(
    "Sepal Length",
    4.0,
    8.0,
    5.0
)

sepal_width = st.sidebar.slider(
    "Sepal Width",
    2.0,
    5.0,
    3.0
)

petal_length = st.sidebar.slider(
    "Petal Length",
    1.0,
    7.0,
    1.5
)

petal_width = st.sidebar.slider(
    "Petal Width",
    0.1,
    3.0,
    0.2
)

if st.button("Predict"):

    X = np.array([
        [
            sepal_length,
            sepal_width,
            petal_length,
            petal_width
        ]
    ])

    prediction = model.predict(X)

    st.success(
        f"Predicted class: {prediction[0]}"
    )
```

This gives you:

```text
                Iris Classifier

Sidebar                         Main
─────────────                   ───────────────

Sepal Length                    🌸 Prediction
[──────●────]

Sepal Width                     Predicted:
[────●─────]                    Setosa

Petal Length

Petal Width

[ Predict ]
```

---

# 30. Better ML UI Architecture

For serious ML projects, don't put everything into one huge `app.py`.

Use:

```text
ml_app/
│
├── app.py
│
├── models/
│   └── model.pkl
│
├── utils/
│   ├── preprocessing.py
│   └── prediction.py
│
├── pages/
│   ├── prediction.py
│   ├── analytics.py
│   └── about.py
│
└── requirements.txt
```

Or, with the newer navigation approach:

```text
ml_app/
│
├── app.py
├── pages/
│   ├── prediction.py
│   ├── analytics.py
│   └── about.py
│
├── models/
├── utils/
└── data/
```

Streamlit currently recommends `st.Page` + `st.navigation` when you want a more customizable multipage architecture. The simpler `pages/` directory approach is still available. ([Streamlit Docs][5])

---

# 31. Modern Multipage Application

Example:

```python
# app.py

import streamlit as st

st.set_page_config(
    page_title="ML Dashboard",
    page_icon="🤖",
    layout="wide"
)

prediction_page = st.Page(
    "pages/prediction.py",
    title="Prediction",
    icon="🤖"
)

analytics_page = st.Page(
    "pages/analytics.py",
    title="Analytics",
    icon="📊"
)

about_page = st.Page(
    "pages/about.py",
    title="About",
    icon="ℹ️"
)

pg = st.navigation([
    prediction_page,
    analytics_page,
    about_page
])

pg.run()
```

This gives you a proper application navigation system.

---

# 32. Designing an ML Dashboard

A good ML dashboard might look like:

```text
┌─────────────────────────────────────────────────────────┐
│ 🤖 ML Prediction Dashboard                              │
├───────────────┬─────────────────────────────────────────┤
│               │                                         │
│ Navigation    │  Model Performance                      │
│               │                                         │
│ Dashboard     │ ┌────────┐ ┌────────┐ ┌────────┐       │
│ Prediction    │ │Accuracy│ │ F1     │ │ ROC-AUC│       │
│ Analytics     │ │ 94.5%  │ │ 92.1%  │ │ 0.96   │       │
│ Dataset       │ └────────┘ └────────┘ └────────┘       │
│               │                                         │
│               │  Prediction                             │
│               │ ┌─────────────────────────────────────┐ │
│               │ │ Feature 1      [────────●──]       │ │
│               │ │ Feature 2      [────●──────]       │ │
│               │ │ Feature 3      [──────────●]       │ │
│               │ │                                     │ │
│               │ │       [ Predict ]                   │ │
│               │ └─────────────────────────────────────┘ │
│               │                                         │
└───────────────┴─────────────────────────────────────────┘
```

The main UI building blocks are:

```text
st.sidebar
     ↓
st.columns()
     ↓
st.metric()
     ↓
st.container()
     ↓
st.form()
     ↓
st.tabs()
     ↓
st.dataframe()
     ↓
st.chart()
```

---

# 33. Caching ML Models

This is **very important** for ML applications.

Suppose:

```python
model = joblib.load("model.pkl")
```

is executed every time Streamlit reruns.

That's inefficient.

Use:

```python
@st.cache_resource
def load_model():

    model = joblib.load("model.pkl")

    return model


model = load_model()
```

Streamlit provides two major caching mechanisms:

```text
@st.cache_data
        ↓
Data/results

@st.cache_resource
        ↓
Resources such as ML models
```

The official documentation recommends `st.cache_data` for data-producing computations and `st.cache_resource` for global resources such as models and database connections. ([Streamlit Docs][6])

---

# 34. `st.cache_data`

Suppose you're loading a dataset:

```python
@st.cache_data
def load_data():

    return pd.read_csv("data.csv")
```

Then:

```python
df = load_data()
```

This avoids unnecessarily repeating expensive data-loading operations.

---

# 35. ML Prediction Architecture

A good Streamlit ML application can follow:

```text
                   Streamlit UI
                        │
          ┌─────────────┴─────────────┐
          │                           │
       Inputs                       Upload
          │                           │
          └─────────────┬─────────────┘
                        ↓
                 Preprocessing
                        ↓
                  ML Pipeline
                        ↓
                     Model
                        ↓
                  Prediction
                        ↓
                Visualization
```

For example:

```python
@st.cache_resource
def load_model():

    return joblib.load("model.pkl")


model = load_model()


def predict(features):

    prediction = model.predict(features)

    return prediction
```

Then UI:

```python
age = st.number_input("Age")
income = st.number_input("Income")

if st.button("Predict"):

    features = [[age, income]]

    prediction = predict(features)

    st.success(f"Prediction: {prediction[0]}")
```

This separates:

```text
UI
Logic
Model
```

which is much cleaner.

---

# 36. ML Project Example — Customer Churn

Imagine your model predicts whether a customer will churn.

Your UI could be:

```text
Customer Churn Prediction
─────────────────────────────────────────

Customer Information

Age             [ 32       ]
Tenure          [ 24       ]
Monthly Charges [ 150.50   ]

Contract        [ Month-to-month ▼ ]

Internet        [ Fiber optic ▼ ]

Support Calls   [ 3        ]


             [ Predict Churn ]


Prediction
─────────────────────────────────────────

⚠️ Customer likely to churn

Probability:

████████████████░░░░ 78%
```

Implementation:

```python
import streamlit as st
import numpy as np
import joblib

@st.cache_resource
def load_model():
    return joblib.load("churn_model.pkl")


model = load_model()

st.title("Customer Churn Prediction")

with st.form("churn_form"):

    age = st.number_input(
        "Age",
        min_value=18,
        max_value=100
    )

    tenure = st.number_input(
        "Tenure",
        min_value=0
    )

    monthly_charges = st.number_input(
        "Monthly Charges",
        min_value=0.0
    )

    contract = st.selectbox(
        "Contract",
        ["Month-to-month", "One year", "Two year"]
    )

    submitted = st.form_submit_button(
        "Predict Churn"
    )

if submitted:

    # preprocessing would happen here

    X = np.array([
        [
            age,
            tenure,
            monthly_charges
        ]
    ])

    prediction = model.predict(X)[0]

    if prediction == 1:

        st.error("Customer is likely to churn.")

    else:

        st.success("Customer is unlikely to churn.")
```

---

# 37. File-Based ML Application

A particularly useful project is:

```text
             Upload CSV
                  ↓
            Data Preview
                  ↓
             Data Cleaning
                  ↓
           Exploratory Analysis
                  ↓
             Feature Selection
                  ↓
             Model Training
                  ↓
           Model Evaluation
                  ↓
             Prediction
```

UI:

```text
┌──────────────────────────────────────────┐
│        ML Dataset Analyzer               │
├──────────────────────────────────────────┤
│                                          │
│ Upload Dataset                           │
│ [ Choose CSV ]                           │
│                                          │
│ Dataset Preview                          │
│ ┌──────────────────────────────────────┐ │
│ │ Age │ Salary │ Experience │ Churn    │ │
│ │ 25  │ 30000  │ 2          │ 0        │ │
│ │ 31  │ 50000  │ 5          │ 1        │ │
│ └──────────────────────────────────────┘ │
│                                          │
│ [ Analyze Dataset ]                      │
│                                          │
│ Rows: 5000                               │
│ Columns: 12                              │
│ Missing: 43                              │
│                                          │
└──────────────────────────────────────────┘
```

---

# 38. Building EDA UI

You can combine Streamlit with Pandas, Matplotlib, Seaborn and Plotly.

Example:

```python
uploaded_file = st.file_uploader(
    "Upload CSV",
    type=["csv"]
)

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    st.subheader("Dataset")

    st.dataframe(df)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Rows", df.shape[0])

    with col2:
        st.metric("Columns", df.shape[1])

    with col3:
        st.metric(
            "Missing Values",
            df.isnull().sum().sum()
        )
```

Then:

```python
st.subheader("Numerical Summary")

st.dataframe(df.describe())
```

Then:

```python
st.subheader("Correlation")

corr = df.corr(numeric_only=True)

st.dataframe(corr)
```

---

# 39. Important UI Design Principle

Don't make everything appear at once.

Bad:

```text
Dataset
Statistics
30 charts
Model
Prediction
Parameters
Logs
Feature importance
Confusion matrix
...
```

Better:

```text
Sidebar
│
├── Dashboard
├── Dataset
├── EDA
├── Training
├── Evaluation
└── Prediction
```

Then each section has a clear purpose.

---

# 40. Streamlit + ML Learning Path

Since you're learning ML, I recommend learning Streamlit in this order:

### Level 1 — Fundamentals

Learn:

```text
st.write
st.title
st.header
st.markdown
st.dataframe
```

### Level 2 — Inputs

Learn:

```text
st.button
st.text_input
st.number_input
st.slider
st.selectbox
st.radio
st.checkbox
st.multiselect
st.file_uploader
```

### Level 3 — Layout

Learn:

```text
st.sidebar
st.columns
st.container
st.tabs
st.expander
st.empty
```

### Level 4 — Forms

Learn:

```text
st.form
st.form_submit_button
```

### Level 5 — State

Learn:

```text
st.session_state
callbacks
keys
```

This is especially important because Streamlit reruns the script after interactions. ([Streamlit Docs][2])

### Level 6 — Performance

Learn:

```text
st.cache_data
st.cache_resource
```

([Streamlit Docs][6])

### Level 7 — Visualization

Learn:

```text
st.line_chart
st.bar_chart
st.area_chart
st.pyplot
Plotly
Altair
```

### Level 8 — Application Architecture

Learn:

```text
Multipage apps
st.Page
st.navigation
Reusable components
Utility functions
Model loading
Database connections
```

### Level 9 — Deployment

Finally:

```text
Local Streamlit
      ↓
GitHub
      ↓
Streamlit deployment / cloud
```

---

# 41. The Most Important Concepts to Master

If your goal is **ML/AI application development**, don't try to memorize every Streamlit function.

Focus heavily on these:

```text
                 STREAMLIT
                     │
       ┌─────────────┼─────────────┐
       ↓             ↓             ↓
      UI           STATE         DATA
       │             │             │
       ↓             ↓             ↓
   widgets     session_state   dataframe
   columns     callbacks       charts
   sidebar                     upload
   forms
       │             │             │
       └─────────────┼─────────────┘
                     ↓
                 ML MODEL
                     │
                     ↓
                PREDICTION
                     │
                     ↓
                VISUALIZATION
```

The **three concepts I would prioritize most** are:

1. **Widgets + layouts** — how to build the interface.
2. **Session State + rerun model** — how to make the application behave correctly.
3. **Caching** — how to make ML applications fast.

Once those are comfortable, move into **multipage architecture, reusable components, model serving, database integration, authentication, and deployment**.

For the current Streamlit API, the official documentation's fundamentals and layout guides are good references, especially for the execution model, state, caching, layouts, and multipage applications. ([Streamlit Docs][7])

### A very good next project

Build an **End-to-End ML Dashboard**:

```text
                    ML DASHBOARD
                         │
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
    Dashboard         Dataset         Prediction
        │                │                │
    Metrics          Upload CSV        Inputs
    Charts           Preview           Form
    Model info       Cleaning           │
        │                │               ↓
        │                │             Model
        │                │               │
        └────────────────┼───────────────┘
                         ↓
                   Results / Charts
```

That single project will force you to learn almost every Streamlit concept that actually matters for **ML application development**.

[1]: https://docs.streamlit.io/get-started/fundamentals/summary?utm_source=chatgpt.com "App model summary - Streamlit Docs"
[2]: https://docs.streamlit.io/develop/concepts/architecture/session-state?utm_source=chatgpt.com "Add statefulness to apps - Streamlit Docs"
[3]: https://docs.streamlit.io/develop/concepts/architecture?utm_source=chatgpt.com "Working with Streamlit's execution model - Streamlit Docs"
[4]: https://docs.streamlit.io/develop/concepts/design/layouts-and-containers?utm_source=chatgpt.com "Using layouts and containers - Streamlit Docs"
[5]: https://docs.streamlit.io/develop/concepts/multipage-apps/overview?utm_source=chatgpt.com "Overview of multipage apps - Streamlit Docs"
[6]: https://docs.streamlit.io/develop/api-reference/caching-and-state?utm_source=chatgpt.com "Caching and state - Streamlit Docs"
[7]: https://docs.streamlit.io/get-started/fundamentals?utm_source=chatgpt.com "Fundamental concepts - Streamlit Docs"
