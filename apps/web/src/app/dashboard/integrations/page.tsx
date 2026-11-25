'use client';

import * as React from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Plug, RefreshCw, Trash2, FlaskConical, RotateCw, ShieldAlert } from 'lucide-react';

type Integration={id:string;type:string;name:string;is_active:boolean;last_sync_at?:string|null;last_sync_status:string;last_sync_error?:string|null;campaign_id?:string|null;config?:Record<string,any>};
export default function IntegrationsPage(){
 const [items,setItems]=React.useState<Integration[]>([]);
 const [loading,setLoading]=React.useState(true);
 const [busy,setBusy]=React.useState('');
 const [error,setError]=React.useState('');
 const [notice,setNotice]=React.useState('');
 const [showTwilio,setShowTwilio]=React.useState(false);
 const [twilio,setTwilio]=React.useState({account_sid:'',auth_token:'',phone_number:''});
 const load=React.useCallback(async()=>{try{setError('');const rows=await api.get<Integration[]>('/integrations');setItems(Array.isArray(rows)?rows:[]);}catch(e){setError(e instanceof Error?e.message:'Unable to load integrations.');}finally{setLoading(false);}},[]);
 React.useEffect(()=>{void load();const t=window.setInterval(()=>void load(),30000);return()=>window.clearInterval(t);},[load]);
 async function connectTwilio(e:React.FormEvent){
  e.preventDefault();setBusy('twilio');setError('');setNotice('');
  try{
   const created=await api.post<Integration>('/integrations',{type:'TWILIO',name:'Twilio Voice',config:twilio});
   const test=await api.post<any>('/integrations/'+created.id+'/test');
   if(test?.success===false)throw new Error(test.error||'Twilio credentials could not be verified. The integration was saved; check the details and test again.');
   setNotice(test?.message||'Twilio connected successfully.');
   setTwilio({account_sid:'',auth_token:'',phone_number:''});setShowTwilio(false);await load();
  }catch(e){setError(e instanceof Error?e.message:'Twilio setup failed.');}finally{setBusy('');}
 }
 async function run(id:string,action:'test'|'sync'|'delete'){
  if(action==='delete'&&!window.confirm('Remove this integration from the workspace?'))return;
  setBusy(id+action);setError('');setNotice('');
  try{if(action==='delete'){await api.delete('/integrations/'+id);setNotice('Integration removed.');}else{const result=await api.post<any>('/integrations/'+id+'/'+action);if(result?.success===false)throw new Error(result.error||'The provider request failed.');setNotice(result?.message||(action==='test'?'Connection test succeeded.':'Sync request completed.'));}await load();}
  catch(e){setError(e instanceof Error?e.message:'Integration action failed.');}finally{setBusy('');}
 }
 return <DashboardLayout><div className="mx-auto max-w-[1400px] space-y-6">
  <header className="flex flex-wrap items-center justify-between gap-3"><h1 className="text-3xl font-bold tracking-tight">Integrations</h1><div className="flex gap-2"><Button onClick={()=>setShowTwilio(v=>!v)}>{showTwilio?'Close':'Connect Twilio'}</Button><Button variant="outline" onClick={()=>{setLoading(true);void load();}} disabled={loading}><RefreshCw className={'mr-2 h-4 w-4 '+(loading?'animate-spin':'')}/>Refresh</Button></div></header>
  <div className="flex gap-3 rounded-2xl border border-info/20 bg-info/5 p-4 text-sm"><ShieldAlert className="mt-0.5 h-4 w-4 shrink-0 text-info"/><p className="text-base-content/65">Twilio credentials are encrypted by the backend before storage. The Auth Token is never shown again in the dashboard. Configure a voice-enabled Twilio number in E.164 format, such as +14155550123.</p></div>
  {showTwilio&&<Card className="border-base-300/80"><CardHeader><CardTitle className="text-base">Twilio voice setup</CardTitle><p className="text-xs text-base-content/50">Find the Account SID and Auth Token in your Twilio Console.</p></CardHeader><CardContent><form onSubmit={connectTwilio} className="grid gap-3 md:grid-cols-2">
   <label className="space-y-1 text-xs font-semibold">Account SID<input required value={twilio.account_sid} onChange={e=>setTwilio({...twilio,account_sid:e.target.value.trim()})} placeholder="AC…" className="mt-1 h-10 w-full rounded-xl border border-base-300 bg-base-200/50 px-3 text-sm font-normal"/></label>
   <label className="space-y-1 text-xs font-semibold">Auth Token<input required type="password" autoComplete="new-password" value={twilio.auth_token} onChange={e=>setTwilio({...twilio,auth_token:e.target.value})} className="mt-1 h-10 w-full rounded-xl border border-base-300 bg-base-200/50 px-3 text-sm font-normal"/></label>
   <label className="space-y-1 text-xs font-semibold md:col-span-2">Outgoing phone number<input required value={twilio.phone_number} onChange={e=>setTwilio({...twilio,phone_number:e.target.value.trim()})} placeholder="+14155550123" className="mt-1 h-10 w-full rounded-xl border border-base-300 bg-base-200/50 px-3 text-sm font-normal"/><span className="font-normal text-base-content/45">Use a Twilio number with Programmable Voice enabled.</span></label>
   <div className="flex justify-end md:col-span-2"><Button type="submit" disabled={busy==='twilio'}>{busy==='twilio'?'Connecting…':'Save and test Twilio'}</Button></div>
  </form></CardContent></Card>}
  {error&&<div role="alert" className="rounded-xl border border-error/25 bg-error/5 px-4 py-3 text-sm text-error">{error}</div>}{notice&&<div role="status" className="rounded-xl border border-success/25 bg-success/5 px-4 py-3 text-sm text-success">{notice}</div>}
  {loading&&items.length===0?<Card className="p-12 text-center text-sm text-base-content/50">Loading integrations…</Card>:items.length===0?<Card className="px-6 py-16 text-center"><Plug className="mx-auto h-8 w-8 text-base-content/25"/><p className="mt-3 font-semibold">No integrations connected</p><p className="mt-1 text-sm text-base-content/50">Connect Twilio to configure the outgoing caller ID for your campaigns.</p><Button className="mt-4" onClick={()=>setShowTwilio(true)}>Connect Twilio</Button></Card>:<div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{items.map(item=><Card key={item.id} className="border-base-300/80 shadow-sm"><CardHeader><div className="flex items-start justify-between gap-3"><div className="flex items-center gap-3"><span className="grid h-11 w-11 place-items-center rounded-xl bg-primary/10 text-primary"><Plug className="h-5 w-5"/></span><div><CardTitle className="text-base">{item.name}</CardTitle><p className="mt-1 text-[10px] font-semibold tracking-wide text-base-content/45">{item.type.replaceAll('_',' ')}</p></div></div><Badge variant={item.is_active?'success':'outline'}>{item.is_active?'Active':'Disabled'}</Badge></div></CardHeader><CardContent><div className="space-y-2 rounded-xl bg-base-200/50 p-3 text-xs">{item.type==='TWILIO'&&<div className="flex justify-between gap-2"><span className="text-base-content/45">Caller ID</span><span>{item.config?.phone_number||'Not set'}</span></div>}<div className="flex justify-between gap-2"><span className="text-base-content/45">Last sync</span><span>{item.last_sync_at?new Date(item.last_sync_at).toLocaleString():'Never'}</span></div><div className="flex justify-between gap-2"><span className="text-base-content/45">Sync status</span><span>{item.last_sync_status}</span></div>{item.last_sync_error&&<p className="line-clamp-2 text-error">{item.last_sync_error}</p>}</div><div className="mt-4 flex flex-wrap gap-2"><Button size="sm" variant="outline" disabled={!!busy} onClick={()=>void run(item.id,'test')}><FlaskConical className="mr-1.5 h-3.5 w-3.5"/>Test</Button><Button size="sm" variant="outline" disabled={!!busy||!item.is_active||item.type==='TWILIO'} onClick={()=>void run(item.id,'sync')}><RotateCw className="mr-1.5 h-3.5 w-3.5"/>Sync</Button><Button size="icon" variant="ghost" aria-label="Remove integration" disabled={!!busy} onClick={()=>void run(item.id,'delete')}><Trash2 className="h-4 w-4 text-error"/></Button></div></CardContent></Card>)}</div>}
 </div></DashboardLayout>;
}
