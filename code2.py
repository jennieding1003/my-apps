import streamlit as st
import numpy as np
from scipy.optimize import newton

# 自定义 CSS 样式
st.markdown(
    """
    <style>
    body {
        background-color: #f5f5f5;
        font-family: sans-serif;
    }
    .stApp {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
    .stTextInput > label,
    .stNumberInput > label,
    .stRadio > label,
    .stButton > button {
        color: #333;
    }
    .stTextInput > div > input,
    .stNumberInput > div > input {
        border: 1px solid #ccc;
        border-radius: 0.25rem;
        padding: 0.5rem;
    }
    .stButton > button {
        background-color: #0078d4;
        color: white;
        border: none;
        border-radius: 0.25rem;
        padding: 0.5rem 1rem;
        cursor: pointer;
    }
    .stButton > button:hover {
        background-color: #005a9e;
    }
    .stSuccess {
        color: #28a745;
    }
    .stInfo {
        color: #17a2b8;
    }
    .stError {
        color: #dc3545;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def calculate_irr(initial_investment, cash_flows, discount_rate):
    """计算现金流的内部收益率 (IRR)。"""
    cash_flows_with_initial = [-initial_investment] + cash_flows  # 投资额作为第0期，且为负值
    try:
        irr = newton(lambda r: np.sum(np.array(cash_flows_with_initial) / (1 + r)**np.arange(len(cash_flows_with_initial))), discount_rate)
        return irr
    except RuntimeError:
        return None  # 迭代未收敛

def calculate_present_value(initial_investment, cash_flows, discount_rate):
    """计算现金流的现值 (PV)。"""
    cash_flows_with_initial = [-initial_investment] + cash_flows # 投资额作为第0期，且为负值
    pv = np.sum(np.array(cash_flows_with_initial) / (1 + discount_rate)**np.arange(len(cash_flows_with_initial)))
    return pv

def main():
    st.title("现金流回报率 (IRR) 计算器")

    # 计算逻辑说明
    with st.expander("计算逻辑说明", expanded=False):  # 默认收起
        st.write("""
        **计算公式:**

        *   **NPV (净现值):**
            NPV = Σ [CFt / (1 + r)^t], t=0,1,2,...N

        *   **IRR (内部收益率):**
             求解 r 使 NPV = 0

        *   **PV (现值):**
            PV = Σ [CFt / (1 + r)^t], t=0,1,2,...N

        其中:
            * CFt = 第 t 期的现金流
            * r = 贴现率 (IRR)
            * N = 总期数

        **贴现率转换公式:**

        *   **年贴现率 -> 月贴现率:**
            月贴现率 = (1 + 年贴现率)^(1/12) - 1

        *   **月IRR -> 年IRR:**
            年IRR = (1 + 月IRR)^12 - 1
        """)

    # 1. 增加周期选择 (下拉选择框)
    period_type = st.selectbox("周期:", ("月", "年"), index=0, help="选择现金流的周期，按月或按年")  # 默认为月，增加浮窗

    # 5. 年贴现率提前
    annual_discount_rate = st.number_input("年贴现率 (%):", min_value=0.0, value=10.0, step=1.0, help="以百分比表示的年贴现率")  # 添加浮窗
    annual_discount_rate /= 100  # 转换为小数

    # 4. 统一现金流选择 (下拉选择框，默认 "是")
    uniform_cash_flow = st.selectbox("统一现金流:", ("是", "否"), index=0, help="选择是否使用统一的现金流，是则每期都相同，否可以每期单独调整")  # 默认为“是”，添加浮窗

    # 2. & 3. 投资额和期数输入 (投资额显示为正，但计算时为负值)
    col1, col2 = st.columns(2)
    with col1:
        initial_investment = st.number_input("投资额 (元):", min_value=0.0, value=10000.0, step=1000.0, help="初始投资金额，显示为正数，计算时自动转为负数") # 添加浮窗
    with col2:
        num_periods = st.number_input("期数:", min_value=1, value=12, step=1, help="现金流的期数，不包括第0期投资")  # 添加浮窗

    cash_flows = []
    if uniform_cash_flow == "是":
        # 单一现金流输入
        cash_flow_value = st.number_input("每期现金流 (元):", value=500.0, step=100.0, help="所有期数都相同的现金流") # 添加浮窗
        cash_flows = [cash_flow_value] * num_periods
    else:
        # 每期现金流输入
        uniform_value = st.number_input("统一赋值 (元):", value=500.0, step=100.0, help="用于快速为所有期数赋值的统一值") # 添加浮窗
        cash_flows = [uniform_value] * num_periods
        st.write("请输入每期现金流 (元):")
        for i in range(num_periods):
            cash_flow = st.number_input(f"第 {i+1} 期现金流:", value=cash_flows[i], step=100.0, key=f"cash_flow_{i}", help=f"第 {i+1} 期的现金流")  # 添加浮窗
            cash_flows[i] = cash_flow

    monthly_discount_rate = (1 + annual_discount_rate)**(1/12) - 1 if period_type == "月" else annual_discount_rate

    # 6. 计算按钮
    if st.button("计算", key = "calculate_button"):  # 添加key防止与计算按钮冲突
        # 7 & 8. 计算 IRR 和 PV
        if len(cash_flows) != num_periods:
            st.error("现金流的数量需要和期数一致!")
            return

        irr = calculate_irr(initial_investment, cash_flows, monthly_discount_rate if period_type == "月" else annual_discount_rate) # 根据周期选择贴现率

        if irr is not None:
            if period_type == "月":
                annual_irr = (1 + irr)**12 - 1
                # 1. 显示月贴现率
                st.success(f"月贴现率: {monthly_discount_rate:.4%}")
                st.success(f"月 IRR: {irr:.2%} (年化: {annual_irr:.2%})")
                present_value = calculate_present_value(initial_investment, cash_flows, monthly_discount_rate)
            else:  # period_type == "年"
                st.success(f"年 IRR: {irr:.2%}")
                present_value = calculate_present_value(initial_investment, cash_flows, annual_discount_rate) # 根据周期选择贴现率

            st.info(f"现金流现值 (PV): {present_value:.2f} 元")
        else:
            st.error("无法计算 IRR。请检查输入或调整贴现率。")

if __name__ == "__main__":
    main()