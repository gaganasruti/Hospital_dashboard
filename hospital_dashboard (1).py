import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title='Healthcare Appointment No-Show Analytics',page_icon='🏥',layout='wide',initial_sidebar_state='expanded')

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:"DM Sans",sans-serif;background-color:#1a1d27!important;color:#e8ecf4!important;}
[data-testid="stSidebar"]{background-color:#1e2235!important;border-right:1px solid #2e3455;}
[data-testid="stSidebar"] *{color:#e8ecf4!important;}
.stSelectbox>div>div,.stMultiSelect>div>div{background-color:#22263a!important;border:1px solid #2e3455!important;border-radius:8px!important;}
[data-testid="stTabs"] [role="tablist"]{background:#22263a;border-radius:14px;padding:4px;gap:4px;border:1px solid #2e3455;}
[data-testid="stTabs"] [role="tab"]{border-radius:10px!important;color:#8892a4!important;font-weight:500;font-size:.85rem;padding:8px 20px!important;transition:all .2s;}
[data-testid="stTabs"] [role="tab"][aria-selected="true"]{background:#4f8ef7!important;color:#fff!important;}
hr{border-color:#2e3455!important;}
</style>''',unsafe_allow_html=True)

COLORS=["#4f8ef7","#f7884f","#4fcfb0","#f74f7a","#a78bfa","#fbbf24","#34d399"]
CL=dict(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans',color='#e8ecf4',size=12),
        margin=dict(l=10,r=10,t=40,b=10),
        legend=dict(bgcolor='rgba(0,0,0,0)'),
        xaxis=dict(gridcolor='#2e3455',zerolinecolor='#2e3455'),
        yaxis=dict(gridcolor='#2e3455',zerolinecolor='#2e3455'))

def sf(fig): fig.update_layout(**CL); return fig

def kpi(title,value,subtitle='',color='#4f8ef7',icon='📊'):
    return f'''<div style="background:#22263a;border:1px solid #2e3455;border-top:3px solid {color};
    border-radius:14px;padding:20px 22px;min-height:120px;">
    <div style="font-size:.72rem;color:#8892a4;text-transform:uppercase;letter-spacing:.08em;font-weight:600;margin-bottom:6px;">{icon}&nbsp;{title}</div>
    <div style="font-size:2rem;font-weight:700;color:{color};line-height:1.1;">{value}</div>
    <div style="font-size:.78rem;color:#8892a4;margin-top:6px;">{subtitle}</div></div>'''

@st.cache_data
def load(file):
    df=pd.read_csv(file)
    df.columns=df.columns.str.strip().str.upper().str.replace(' ','_').str.replace('-','_')
    # Handle NO_SHOW
    if 'NO_SHOW' in df.columns:
        if df['NO_SHOW'].dtype==object:
            df['NO_SHOW']=df['NO_SHOW'].map({'Yes':1,'No':0,'YES':1,'NO':0}).fillna(df['NO_SHOW'])
        df['NO_SHOW']=pd.to_numeric(df['NO_SHOW'],errors='coerce').fillna(0).astype(int)
    else:
        df['NO_SHOW']=0
    # Rename common variants
    rename={}
    if 'HIPERTENSION' in df.columns: rename['HIPERTENSION']='HYPERTENSION'
    if 'HANDCAP' in df.columns: rename['HANDCAP']='HANDICAP'
    if 'SMS_RECEIVED' in df.columns: rename['SMS_RECEIVED']='SMS_RECEIVED'
    if rename: df=df.rename(columns=rename)
    # Numeric
    for c in ['WAIT_DAYS','AGE','COMORBIDITY_COUNT']:
        if c in df.columns: df[c]=pd.to_numeric(df[c],errors='coerce')
    # Dates
    for c in ['SCHEDULED_DAY','APPOINTMENT_DAY']:
        if c in df.columns: df[c]=pd.to_datetime(df[c],errors='coerce')
    # Derive WAIT_DAYS if missing
    if 'WAIT_DAYS' not in df.columns and 'SCHEDULED_DAY' in df.columns and 'APPOINTMENT_DAY' in df.columns:
        df['WAIT_DAYS']=(df['APPOINTMENT_DAY']-df['SCHEDULED_DAY']).dt.days
    # APPT_DOW_NAME
    if 'APPT_DOW_NAME' not in df.columns and 'APPOINTMENT_DAY' in df.columns:
        df['APPT_DOW_NAME']=df['APPOINTMENT_DAY'].dt.day_name()
    # AGE_GROUP
    if 'AGE_GROUP' not in df.columns and 'AGE' in df.columns:
        bins=[0,12,17,35,60,115]
        labels=['Child','Teen','Young Adult','Adult','Senior']
        df['AGE_GROUP']=pd.cut(df['AGE'],bins=bins,labels=labels)
    # WAIT_GROUP
    if 'WAIT_GROUP' not in df.columns and 'WAIT_DAYS' in df.columns:
        bins=[-1,0,7,30,90,9999]
        labels=['Same Day','1-7 Days','8-30 Days','31-90 Days','90+ Days']
        df['WAIT_GROUP']=pd.cut(df['WAIT_DAYS'],bins=bins,labels=labels)
    # COMORBIDITY_COUNT
    if 'COMORBIDITY_COUNT' not in df.columns:
        cols=[c for c in ['HYPERTENSION','DIABETES','ALCOHOLISM','HANDICAP'] if c in df.columns]
        if cols: df['COMORBIDITY_COUNT']=df[cols].sum(axis=1)
    return df

def filters(df):
    st.sidebar.markdown('''<div style="text-align:center;padding:12px 0 20px;">
    <span style="font-size:1.6rem;">🏥</span><br>
    <span style="font-weight:700;font-size:1.05rem;">Hospital Analytics</span><br>
    <span style="font-size:.72rem;color:#8892a4;">No-Show Dashboard</span>
    </div><hr style="margin:0 0 16px;">''',unsafe_allow_html=True)
    st.sidebar.markdown('### ⚙️ Filters')
    f=df.copy()
    for col,label in [('GENDER','Gender'),('AGE_GROUP','Age Group'),('APPT_DOW_NAME','Appointment Day'),('SCHOLARSHIP','Scholarship'),('SMS_RECEIVED','SMS Received')]:
        if col in df.columns:
            opts=['All']+sorted(df[col].dropna().astype(str).unique().tolist())
            sel=st.sidebar.selectbox(label,opts)
            if sel!='All': f=f[f[col].astype(str)==sel]
    st.sidebar.markdown('---')
    st.sidebar.markdown(f"<small style='color:#8892a4;'>Showing **{len(f):,}** of **{len(df):,}** records</small>",unsafe_allow_html=True)
    return f

def page1(df):
    # Charts row 1: Pie (gender) + Bar (age group)
    c1,c2=st.columns(2)
    with c1:
        if 'GENDER' in df.columns:
            grp=df.groupby('GENDER').size().reset_index(name='Count')
            fig=go.Figure(go.Pie(labels=grp['GENDER'],values=grp['Count'],
                                  marker_colors=['#4f8ef7','#f7884f'],
                                  textinfo='label+percent',hole=0))
            fig.update_layout(title='Appointment Attendance by Gender',**CL)
            st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
    with c2:
        if 'AGE_GROUP' in df.columns:
            order=['Child','Teen','Young Adult','Adult','Senior']
            grp=df.groupby('AGE_GROUP').size().reset_index(name='Total Appointments')
            grp['AGE_GROUP']=pd.Categorical(grp['AGE_GROUP'],categories=order,ordered=True)
            grp=grp.sort_values('AGE_GROUP')
            fig=px.bar(grp,y='AGE_GROUP',x='Total Appointments',orientation='h',
                       color_discrete_sequence=['#4f8ef7'],
                       text='Total Appointments')
            fig.update_traces(texttemplate='%{text:,.0f}',textposition='outside')
            fig.update_layout(title='Total Appointments by AGE_GROUP',**CL)
            st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})

    # Charts row 2: Line (no-show by age) + Bar (missed by SMS)
    c3,c4=st.columns(2)
    with c3:
        if 'AGE' in df.columns:
            grp=df.groupby('AGE')['NO_SHOW'].sum().reset_index()
            grp.columns=['Age','NO_SHOW']
            fig=px.area(grp,x='Age',y='NO_SHOW',color_discrete_sequence=['#4f8ef7'])
            fig.update_layout(title='NO_SHOW Count by Age',**CL)
            st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
    with c4:
        if 'SMS_RECEIVED' in df.columns:
            grp=df.groupby('SMS_RECEIVED')['NO_SHOW'].sum().reset_index()
            grp.columns=['SMS_RECEIVED','Missed Appointments']
            grp['SMS_RECEIVED']=grp['SMS_RECEIVED'].astype(str)
            fig=px.bar(grp,y='SMS_RECEIVED',x='Missed Appointments',orientation='h',
                       color_discrete_sequence=['#4f8ef7'],
                       text='Missed Appointments')
            fig.update_traces(texttemplate='%{text:,.0f}',textposition='outside')
            fig.update_layout(title='Missed Appointments by SMS_RECEIVED',**CL)
            st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})

def page2(df):
    r1=st.columns(2); r2=st.columns(2)
    with r1[0]:
        if 'GENDER' in df.columns:
            grp=df.groupby('GENDER')['NO_SHOW'].mean().mul(100).reset_index()
            grp.columns=['Gender','No-Show Rate']
            fig=px.bar(grp,x='Gender',y='No-Show Rate',color='Gender',
                       color_discrete_sequence=COLORS,text=grp['No-Show Rate'].map('{:.1f}%'.format))
            fig.update_traces(textposition='outside')
            fig.update_layout(showlegend=False,title='No-Show Rate by Gender')
            st.plotly_chart(sf(fig),use_container_width=True,config={'displayModeBar':False})
    with r1[1]:
        conds=[c for c in ['HYPERTENSION','DIABETES','ALCOHOLISM','HANDICAP'] if c in df.columns]
        if conds:
            recs=[]
            for c in conds:
                rate=df[df[c].astype(str).isin(['1','True','yes'])]['NO_SHOW'].mean()*100
                recs.append({'Condition':c.title(),'No-Show Rate':round(rate,1)})
            cdf=pd.DataFrame(recs).sort_values('No-Show Rate')
            fig=px.bar(cdf,y='Condition',x='No-Show Rate',orientation='h',
                       color='Condition',color_discrete_sequence=COLORS,
                       text=cdf['No-Show Rate'].map('{:.1f}%'.format))
            fig.update_traces(textposition='outside')
            fig.update_layout(showlegend=False,title='No-Show Rate by Medical Condition')
            st.plotly_chart(sf(fig),use_container_width=True,config={'displayModeBar':False})
    with r2[0]:
        if 'SMS_RECEIVED' in df.columns:
            grp=df.groupby('SMS_RECEIVED').agg(Total=('NO_SHOW','count'),Showed=('NO_SHOW',lambda x:(x==0).sum())).reset_index()
            grp['Attendance Rate']=grp['Showed']/grp['Total']*100
            grp['SMS_RECEIVED']=grp['SMS_RECEIVED'].astype(str).map({'0':'No SMS','1':'SMS Sent'}).fillna(grp['SMS_RECEIVED'].astype(str))
            fig=px.bar(grp,x='SMS_RECEIVED',y='Attendance Rate',color='SMS_RECEIVED',
                       color_discrete_sequence=['#f74f7a','#4fcfb0'],
                       text=grp['Attendance Rate'].map('{:.1f}%'.format))
            fig.update_traces(textposition='outside')
            fig.update_layout(showlegend=False,title='Attendance Rate by SMS Reminder')
            st.plotly_chart(sf(fig),use_container_width=True,config={'displayModeBar':False})
    with r2[1]:
        if 'COMORBIDITY_COUNT' in df.columns:
            grp=df.groupby('COMORBIDITY_COUNT').agg(Total=('NO_SHOW','count'),NoShows=('NO_SHOW','sum')).reset_index()
            grp['No-Show Rate']=grp['NoShows']/grp['Total']*100
            fig=go.Figure()
            fig.add_bar(x=grp['COMORBIDITY_COUNT'],y=grp['Total'],name='Total Appointments',marker_color='#4f8ef7')
            fig.add_scatter(x=grp['COMORBIDITY_COUNT'],y=grp['No-Show Rate'],name='No-Show Rate %',
                            mode='lines+markers',marker=dict(color='#f74f7a',size=8),
                            line=dict(color='#f74f7a',width=2),yaxis='y2')
            fig.update_layout(title='Appointments & No-Show Rate by Comorbidity',
                              paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                              font=dict(family='DM Sans',color='#e8ecf4',size=12),
                              margin=dict(l=10,r=10,t=40,b=10),
                              yaxis=dict(title='Total',gridcolor='#2e3455'),
                              yaxis2=dict(title='No-Show %',overlaying='y',side='right',gridcolor='#2e3455'),
                              legend=dict(orientation='h',yanchor='bottom',y=1.02,bgcolor='rgba(0,0,0,0)'))
            st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})

def page3(df):
    r1=st.columns(2); r2=st.columns(2)
    with r1[0]:
        if 'WAIT_GROUP' in df.columns:
            order=['Same Day','1-7 Days','8-30 Days','31-90 Days','90+ Days']
            grp=df.groupby('WAIT_GROUP')['NO_SHOW'].mean().mul(100).reset_index()
            grp.columns=['Wait Group','No-Show Rate']
            grp['Wait Group']=pd.Categorical(grp['Wait Group'],categories=order,ordered=True)
            grp=grp.sort_values('Wait Group')
            fig=px.bar(grp,x='Wait Group',y='No-Show Rate',color='No-Show Rate',
                       color_continuous_scale=['#4fcfb0','#f74f7a'],
                       text=grp['No-Show Rate'].map('{:.1f}%'.format))
            fig.update_traces(textposition='outside')
            fig.update_layout(coloraxis_showscale=False,title='No-Show Rate by Wait Group')
            st.plotly_chart(sf(fig),use_container_width=True,config={'displayModeBar':False})
    with r1[1]:
        if 'APPOINTMENT_DAY' in df.columns:
            try:
                df['_D']=pd.to_datetime(df['APPOINTMENT_DAY'],errors='coerce')
                ts=df[df['NO_SHOW']==1].groupby(df['_D'].dt.to_period('W').dt.start_time).size().reset_index()
                ts.columns=['Week','No-Shows']
                fig=px.area(ts,x='Week',y='No-Shows',color_discrete_sequence=['#f74f7a'])
                fig.update_layout(title='No-Show Count Over Time')
                st.plotly_chart(sf(fig),use_container_width=True,config={'displayModeBar':False})
            except: st.info('Could not parse date column.')
    with r2[0]:
        if '_D' in df.columns:
            try:
                ts=df.groupby(df['_D'].dt.to_period('W').dt.start_time).size().reset_index()
                ts.columns=['Week','Appointments']
                fig=px.line(ts,x='Week',y='Appointments',color_discrete_sequence=['#4f8ef7'])
                fig.update_traces(mode='lines+markers',marker=dict(size=5))
                fig.update_layout(title='Total Appointments Over Time')
                st.plotly_chart(sf(fig),use_container_width=True,config={'displayModeBar':False})
            except: pass
    with r2[1]:
        if 'NEIGHBOURHOOD' in df.columns:
            grp=df.groupby('NEIGHBOURHOOD')['NO_SHOW'].mean().mul(100).reset_index()
            grp.columns=['Neighbourhood','No-Show Rate']
            top=grp.nlargest(20,'No-Show Rate').sort_values('No-Show Rate')
            fig=px.bar(top,y='Neighbourhood',x='No-Show Rate',orientation='h',
                       color='No-Show Rate',color_continuous_scale=['#4f8ef7','#f74f7a'],
                       text=top['No-Show Rate'].map('{:.1f}%'.format))
            fig.update_traces(textposition='outside')
            fig.update_layout(coloraxis_showscale=False,height=500,title='No-Show Rate by Neighbourhood (Top 20)')
            st.plotly_chart(sf(fig),use_container_width=True,config={'displayModeBar':False})

def main():
    st.markdown('''<div style="margin-bottom:8px;">
    <span style="font-size:1.5rem;font-weight:700;">🏥 Healthcare Appointment No-Show Analytics Dashboard</span><br>
    <span style="color:#8892a4;font-size:.85rem;">Attendance Intelligence & No-Show Prediction</span>
    </div>''',unsafe_allow_html=True)

    uploaded=st.file_uploader('Upload cleaned.csv or MedicalAppointment.csv',type=['csv'])
    if uploaded is None:
        st.markdown('''<div style="background:#22263a;border:1px dashed #4f8ef7;border-radius:14px;
        padding:40px;text-align:center;margin-top:20px;">
        <div style="font-size:2.5rem;">📂</div>
        <div style="font-size:1.1rem;font-weight:600;margin:10px 0;">Upload your dataset to get started</div>
        <div style="color:#8892a4;font-size:.85rem;">Upload cleaned.csv for best results</div>
        </div>''',unsafe_allow_html=True)
        return

    df=load(uploaded)
    f=filters(df)

    # KPIs matching Power BI
    total=len(f)
    noshow=int(f['NO_SHOW'].sum())
    ns_pct=(noshow/total*100) if total else 0
    avg_age=f['AGE'].mean() if 'AGE' in f.columns else 0
    avg_wait=f['WAIT_DAYS'].mean() if 'WAIT_DAYS' in f.columns else 0

    k1,k2,k3,k4=st.columns(4)
    k1.markdown(kpi('Total Appointments',f'{total:,}','All records in filter','#4f8ef7','📅'),unsafe_allow_html=True)
    k2.markdown(kpi('NO_SHOW Count',f'{noshow:,}','Missed appointments','#f74f7a','🚫'),unsafe_allow_html=True)
    k3.markdown(kpi('No Show %',f'{ns_pct:.2f}%','Of total appointments','#f7884f','📊'),unsafe_allow_html=True)
    k4.markdown(kpi('Avg Age',f'{avg_age:.1f}','Average patient age','#4fcfb0','👤'),unsafe_allow_html=True)
    st.markdown('<br>',unsafe_allow_html=True)
    st.markdown('<hr>',unsafe_allow_html=True)

    tab1,tab2,tab3=st.tabs(['📊  Overview','👥  Patient & Medical','📅  Time & Geography'])
    with tab1: page1(f)
    with tab2: page2(f)
    with tab3: page3(f)

if __name__=='__main__':
    main()
