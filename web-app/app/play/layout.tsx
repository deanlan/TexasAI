import { ReactNode } from "react"
import PlaySideBar from "./_components/play-side-bar"
import PlayTopNav from "./_components/play-top-nav"

export default function PlayLayout({ children }: { children: ReactNode }) {

  return (
    <div className="grid min-h-screen w-full lg:grid-cols-[280px_1fr]">
      <PlaySideBar />
      <PlayTopNav >
        <main className="flex flex-col gap-4 p-4 lg:gap-6">
          {children}
        </main>
      </PlayTopNav>
    </div>
  )
}
