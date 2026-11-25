import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './(dashboard)/providers';

const inter = Inter({ subsets: ['latin'], variable: '--font-sans' });

export const metadata: Metadata = {
  title: 'VoiceAI — Intelligent Voice Operations',
  description: 'Build, launch and improve AI-powered customer conversations with voice agents, campaigns and post-call intelligence.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en" data-theme="voiceai" suppressHydrationWarning><body className={`${inter.variable} font-sans antialiased`}><Providers>{children}</Providers></body></html>;
}
