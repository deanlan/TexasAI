import Provider from '@/app/provider'
import { ThemeProvider } from "@/components/theme-provider"
import { Toaster } from "@/components/ui/sonner"
import { ClerkProvider } from '@clerk/nextjs'
import { Analytics } from "@vercel/analytics/react"
import type { Metadata } from 'next'
import { GeistSans } from 'geist/font/sans';
import './globals.css'
import AuthWrapper from '@/components/wrapper/auth-wrapper'

export const metadata: Metadata = {
  metadataBase: new URL("https://discord.com/invite/N3kad5yx9J"),
  title: {
    default: 'AI Texas Hold\'em Poker ',
    template: `%s | AI Texas`
  },
  openGraph: {
    description: 'Your Best AI Poker tool',
    images: ['']
  },
  twitter: {
    card: 'summary_large_image',
    title: 'AI Texas Hold\'em Poker',
    description: 'Your Best AI Poker tool.',
    siteId: "",
    creator: "@kris",
    creatorId: "",
    images: [''],
  },
}
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <AuthWrapper>
      <html lang="en" suppressHydrationWarning>
        <body className={GeistSans.className}>
          <Provider>
            <ThemeProvider
              attribute="class"
              defaultTheme="system"
              enableSystem
              disableTransitionOnChange
            >
              {children}
              <Toaster />
            </ThemeProvider>
          </Provider>
          <Analytics />
        </body>
      </html>
    </AuthWrapper>
  )
}