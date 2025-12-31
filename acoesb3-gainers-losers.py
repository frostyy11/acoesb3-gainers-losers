import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Maiores Altas e Baixas B3", page_icon="📊", layout="wide")

st.title("📊 Maiores Altas e Baixas - Bolsa Brasil (B3)")
st.markdown("Dados em tempo real das principais ações do Ibovespa")

# Lista das principais ações do Ibovespa
ACOES_B3 = [
    'PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'ABEV3.SA',
    'BBAS3.SA', 'WEGE3.SA', 'RENT3.SA', 'SUZB3.SA', 'RDOR3.SA',
    'RAIL3.SA', 'JBSS3.SA', 'GGBR4.SA', 'HAPV3.SA', 'EMBR3.SA',
    'EQTL3.SA', 'CSAN3.SA', 'CPFE3.SA', 'ELET3.SA', 'CMIG4.SA',
    'CPLE6.SA', 'PETR3.SA', 'VALE5.SA', 'ITUB3.SA', 'BBDC3.SA',
    'B3SA3.SA', 'MGLU3.SA', 'LREN3.SA', 'VIVT3.SA', 'TIMS3.SA',
    'RADL3.SA', 'ASAI3.SA', 'PRIO3.SA', 'CYRE3.SA', 'AZZA3.SA',
    'CMIN3.SA', 'NTCO3.SA', 'KLBN11.SA', 'BRAV3.SA', 'TOTS3.SA',
    'SLCE3.SA', 'BEEF3.SA', 'YDUQ3.SA', 'SBSP3.SA', 'ENBR3.SA',
    'TAEE11.SA', 'SANB11.SA', 'BPAC11.SA', 'GOAU4.SA', 'USIM5.SA',
    'CSNA3.SA', 'BRFS3.SA', 'MRFG3.SA', 'PCAR3.SA', 'SMTO3.SA',
    'MULT3.SA', 'COGN3.SA', 'VBBR3.SA', 'RECV3.SA', 'PETZ3.SA',
    'CRFB3.SA', 'ALOS3.SA', 'LWSA3.SA', 'SOMA3.SA', 'AURE3.SA'
]

@st.cache_data(ttl=300)
def fetch_stock_data():
    """Busca dados das ações brasileiras"""
    data_list = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, ticker in enumerate(ACOES_B3):
        try:
            status_text.text(f"Carregando {ticker}... ({idx+1}/{len(ACOES_B3)})")
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period='2d')
            
            if len(hist) >= 2 and 'regularMarketPrice' in info:
                prev_close = hist['Close'].iloc[-2] if len(hist) >= 2 else hist['Close'].iloc[-1]
                current_price = info.get('regularMarketPrice', hist['Close'].iloc[-1])
                change_pct = ((current_price - prev_close) / prev_close) * 100
                
                data_list.append({
                    'Ticker': ticker.replace('.SA', ''),
                    'Nome': info.get('longName', ticker.replace('.SA', '')),
                    'Preço Atual': current_price,
                    'Variação 24h (%)': change_pct,
                    'Volume': info.get('volume', 0),
                    'Valor de Mercado': info.get('marketCap', 0)
                })
            
            progress_bar.progress((idx + 1) / len(ACOES_B3))
        except Exception as e:
            continue
    
    progress_bar.empty()
    status_text.empty()
    
    if data_list:
        df = pd.DataFrame(data_list)
        df = df.sort_values('Variação 24h (%)', ascending=False).reset_index(drop=True)
        return df
    return None

with st.spinner("Buscando dados da B3..."):
    df = fetch_stock_data()

if df is not None and not df.empty:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_change = df['Variação 24h (%)'].mean()
        st.metric("Variação Média", f"{avg_change:.2f}%")
    
    with col2:
        altas_count = len(df[df['Variação 24h (%)'] > 0])
        st.metric("Em Alta", altas_count, delta=f"{(altas_count/len(df)*100):.0f}%")
    
    with col3:
        baixas_count = len(df[df['Variação 24h (%)'] < 0])
        st.metric("Em Baixa", baixas_count, delta=f"{(baixas_count/len(df)*100):.0f}%")
    
    st.markdown("---")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("🚀 Maiores Altas do Dia")
        altas = df.head(10)
        
        for idx, row in altas.iterrows():
            with st.container():
                c1, c2, c3 = st.columns([2, 2, 1])
                with c1:
                    st.markdown(f"**{row['Ticker']}**")
                    st.caption(row['Nome'][:30] + "..." if len(row['Nome']) > 30 else row['Nome'])
                with c2:
                    st.markdown(f"R$ {row['Preço Atual']:.2f}")
                with c3:
                    st.markdown(f"<span style='color: #00ff00; font-weight: bold;'>+{row['Variação 24h (%)']:.2f}%</span>", unsafe_allow_html=True)
                st.markdown("---")
    
    with col_right:
        st.subheader("📉 Maiores Baixas do Dia")
        baixas = df.tail(10).sort_values('Variação 24h (%)')
        
        for idx, row in baixas.iterrows():
            with st.container():
                c1, c2, c3 = st.columns([2, 2, 1])
                with c1:
                    st.markdown(f"**{row['Ticker']}**")
                    st.caption(row['Nome'][:30] + "..." if len(row['Nome']) > 30 else row['Nome'])
                with c2:
                    st.markdown(f"R$ {row['Preço Atual']:.2f}")
                with c3:
                    st.markdown(f"<span style='color: #ff0000; font-weight: bold;'>{row['Variação 24h (%)']:.2f}%</span>", unsafe_allow_html=True)
                st.markdown("---")
    
    st.markdown("---")
    st.subheader("📋 Todas as Ações")
    
    display_df = df.copy()
    display_df['Preço Atual'] = display_df['Preço Atual'].apply(lambda x: f"R$ {x:.2f}")
    display_df['Volume'] = display_df['Volume'].apply(lambda x: f"{x:,.0f}")
    display_df['Valor de Mercado'] = display_df['Valor de Mercado'].apply(lambda x: f"R$ {x:,.0f}" if x > 0 else "N/A")
    display_df['Variação 24h (%)'] = display_df['Variação 24h (%)'].apply(lambda x: f"{x:+.2f}%")
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=400
    )
    
    st.caption(f"Dados atualizados em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} • Atualiza a cada 5 minutos")
    
    if st.button("🔄 Atualizar Dados"):
        st.cache_data.clear()
        st.rerun()
else:
    st.error("Não foi possível carregar os dados das ações. Tente novamente mais tarde.")

st.markdown("---")
st.caption("💡 **Aviso:** Este aplicativo é apenas para fins informativos. Não constitui recomendação de investimento.")
