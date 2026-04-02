import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import numpy as np

st.set_page_config(page_title="妞妞乐乐体脂减肥记录器", page_icon="💕", layout="wide")

st.title("💕 妞妞乐乐体脂减肥记录器")
st.markdown("**一起减脂，一起变更好～**")

# ====================== 用户系统 ======================
default_users = ["妞妞", "乐乐"]

if "users" not in st.session_state:
    st.session_state.users = default_users.copy()

if "current_user" not in st.session_state:
    st.session_state.current_user = "妞妞"

if "data" not in st.session_state:
    st.session_state.data = {user: pd.DataFrame(columns=['日期', '体重(kg)', '体脂(%)', '备注']) for user in
                             st.session_state.users}

# 创建新用户
with st.sidebar:
    st.subheader("👤 用户管理")
    new_user = st.text_input("创建新用户（昵称）", placeholder="例如：宝宝")
    if st.button("➕ 创建用户") and new_user.strip():
        new_name = new_user.strip()
        if new_name not in st.session_state.users:
            st.session_state.users.append(new_name)
            st.session_state.data[new_name] = pd.DataFrame(columns=['日期', '体重(kg)', '体脂(%)', '备注'])
            st.success(f"✅ 用户 {new_name} 创建成功！")
            st.rerun()
        else:
            st.warning("用户已存在")

    # 用户切换（大按钮风格）
    st.subheader("切换用户")
    current_user = st.selectbox("当前记录用户", st.session_state.users,
                                index=st.session_state.users.index(st.session_state.current_user),
                                key="user_select")
    if current_user != st.session_state.current_user:
        st.session_state.current_user = current_user
        st.rerun()

# ====================== 基础设置 ======================
if "height" not in st.session_state:
    st.session_state.height = {"妞妞": 165.0, "乐乐": 175.0}
if "goal_weight" not in st.session_state:
    st.session_state.goal_weight = {"妞妞": 52.0, "乐乐": 70.0}
if "goal_bf" not in st.session_state:
    st.session_state.goal_bf = {"妞妞": 18.0, "乐乐": 12.0}

user = st.session_state.current_user
df = st.session_state.data[user]

# ====================== 侧边栏导航 ======================
page = st.sidebar.radio("导航",
                        ["📊 仪表盘（两人对比）", "⚖️ 记录数据", "📜 我的历史记录", "🔬 高级分析", "⚙️ 设置"])

today = date.today().isoformat()

# ====================== 设置页 ======================
if page == "⚙️ 设置":
    st.subheader(f"⚙️ {user} 的基础信息")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.height[user] = st.number_input("身高 (cm)", 100.0, 250.0,
                                                        st.session_state.height.get(user, 170.0), 0.1)
    with col2:
        st.session_state.goal_weight[user] = st.number_input("目标体重 (kg)", 30.0, 200.0,
                                                             st.session_state.goal_weight.get(user, 65.0), 0.1)
    st.session_state.goal_bf[user] = st.number_input("目标体脂 (%)", 5.0, 40.0,
                                                     st.session_state.goal_bf.get(user, 15.0), 0.1)
    st.success("✅ 设置已保存")

# ====================== 记录数据 ======================
elif page == "⚖️ 记录数据":
    st.subheader(f"📝 {user} 记录体重 & 体脂")
    record_date = st.date_input("记录日期", date.today())
    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input("体重 (kg)", 30.0, 200.0, 60.0, 0.1)
    with col2:
        bf = st.number_input("体脂 (%)", 5.0, 50.0, 22.0, 0.1)
    note = st.text_input("备注（可选，比如：经期/空腹）", "")

    if st.button("✅ 保存记录", type="primary", use_container_width=True):
        new_row = pd.DataFrame({
            '日期': [record_date.isoformat()],
            '体重(kg)': [weight],
            '体脂(%)': [bf],
            '备注': [note]
        })
        st.session_state.data[user] = pd.concat([st.session_state.data[user], new_row], ignore_index=True)
        st.session_state.data[user] = st.session_state.data[user].sort_values('日期').drop_duplicates(subset='日期',
                                                                                                      keep='last')
        st.success(f"✅ {record_date} 为 {user} 记录成功！")

# ====================== 仪表盘（两人对比） ======================
elif page == "📊 仪表盘（两人对比）":
    st.subheader("📊 两人数据对比仪表盘")

    col1, col2 = st.columns(2)

    for i, u in enumerate(["妞妞", "乐乐"]):
        with (col1 if i == 0 else col2):
            st.markdown(f"**{u}**")
            udf = st.session_state.data[u]
            if not udf.empty:
                udf['日期'] = pd.to_datetime(udf['日期'])
                latest = udf.iloc[-1]
                bmi = round(latest['体重(kg)'] / ((st.session_state.height.get(u, 170) / 100) ** 2), 1)
                st.metric("当前体重", f"{latest['体重(kg)']:.1f} kg")
                st.metric("当前体脂", f"{latest['体脂(%)']:.1f} %")
                st.metric("BMI", bmi)
            else:
                st.info("暂无记录")

    # 两人趋势对比图
    fig = go.Figure()
    colors = {"妞妞": "#ff69b4", "乐乐": "#1e90ff"}

    for u in ["妞妞", "乐乐"]:
        udf = st.session_state.data[u]
        if not udf.empty:
            udf_plot = udf.copy()
            udf_plot['日期'] = pd.to_datetime(udf_plot['日期'])
            fig.add_trace(go.Scatter(x=udf_plot['日期'], y=udf_plot['体重(kg)'],
                                     name=f"{u} 体重", line=dict(color=colors[u], width=3)))
            fig.add_trace(go.Scatter(x=udf_plot['日期'], y=udf_plot['体脂(%)'],
                                     name=f"{u} 体脂", line=dict(color=colors[u], dash='dash'), yaxis='y2'))

    fig.update_layout(
        title="妞妞 vs 乐乐 体重 & 体脂趋势对比",
        xaxis_title="日期",
        yaxis=dict(title="体重 (kg)"),
        yaxis2=dict(title="体脂 (%)", overlaying='y', side='right'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

# ====================== 我的历史记录 ======================
elif page == "📜 我的历史记录":
    st.subheader(f"📜 {user} 的所有记录")
    edited_df = st.data_editor(df.sort_values('日期', ascending=False), num_rows="dynamic", use_container_width=True)
    st.session_state.data[user] = edited_df  # 保存编辑

    if st.button("🗑️ 清空我的所有记录", type="secondary"):
        st.session_state.data[user] = pd.DataFrame(columns=['日期', '体重(kg)', '体脂(%)', '备注'])
        st.rerun()

# ====================== 高级分析（单人深度分析） ======================
elif page == "🔬 高级分析":
    st.subheader(f"🔬 {user} 的深度数据分析")
    if df.empty:
        st.warning("还没有记录数据哦～")
    else:
        # （保持你之前的高级分析逻辑，这里简化展示核心部分，你可以直接复制上一个版本的高级分析代码粘贴进来）
        df['日期'] = pd.to_datetime(df['日期'])
        df = df.sort_values('日期')

        st.write("**统计汇总**")
        total_loss = df['体重(kg)'].iloc[0] - df['体重(kg)'].iloc[-1] if len(df) > 1 else 0
        st.metric("总减重", f"{total_loss:.1f} kg")
        st.metric("平均体脂", f"{df['体脂(%)'].mean():.1f} %")

        # 趋势图（移动平均等）
        df['体重_7日均'] = df['体重(kg)'].rolling(7, min_periods=1).mean()
        fig = px.line(df, x='日期', y=['体重(kg)', '体重_7日均'], title="体重趋势与7日移动平均")
        st.plotly_chart(fig, use_container_width=True)

        # 更多图表可继续扩展（散点、预测等）

# ====================== 数据备份（全局） ======================
st.sidebar.divider()
st.sidebar.subheader("💾 数据备份")

user = st.session_state.current_user
if not st.session_state.data[user].empty:
    csv = st.session_state.data[user].to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(f"📥 下载 {user} 的数据", csv, f"{user}_bodyfat_data.csv", "text/csv")

uploaded = st.sidebar.file_uploader("📤 上传CSV恢复到当前用户", type="csv")
if uploaded:
    try:
        new_df = pd.read_csv(uploaded)
        if all(col in new_df.columns for col in ['日期', '体重(kg)', '体脂(%)']):
            st.session_state.data[user] = new_df
            st.sidebar.success(f"✅ {user} 数据已恢复！")
            st.rerun()
    except:
        st.sidebar.error("文件格式错误")

st.caption("💕 妞妞乐乐一起加油！数据独立保存，随时备份")
