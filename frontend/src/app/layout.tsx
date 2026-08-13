import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AutoHealQA - Agentic Autonomous QA & Self-Healing Engine',
  description: 'AI-driven test case generation and Playwright self-healing web automation platform.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '24px' }}>
          {children}
        </div>
      </body>
    </html>
  );
}
