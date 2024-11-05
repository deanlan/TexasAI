import { CloudArrowUpIcon, LockClosedIcon, ServerIcon } from '@heroicons/react/20/solid'
import { OrbitingCirclesComponent } from './orbiting-circles'
import { Brain, Computer, Gamepad2, Network } from 'lucide-react'
import { FaBusinessTime } from 'react-icons/fa'

const features = [
  {
    name: 'Unlock Unprecedented Efficiency.',
    description:
      'Unlock efficiency and innovation with our Texas AI robot, streamlining your workflows with preset configurations for swift success.',
    icon: Computer,
  },
  {
    name: 'Empower Your Decision-Making.',
    description: 'Our intelligent robot leverages advanced algorithms to revolutionize problem-solving, enabling you to focus on strategic decisions and push the limits of what \'s possible.',
    icon: Brain,
  },
  {
    name: 'Elevate Your Game.',
    description: 'Dive into a world where advanced automation meets practicality, minimizing setup time so you can concentrate on pioneering your game.',
    icon: Gamepad2,
  },
]

export default function SideBySide() {
  return (
    <div className="overflow-hidden ">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto grid max-w-2xl grid-cols-1 gap-x-8 gap-y-16 sm:gap-y-20 lg:mx-0 lg:max-w-none lg:grid-cols-2">
          <div className="lg:pr-8 lg:pt-4">
            <div className="lg:max-w-lg">
              <p className="mt-2 text-3xl font-bold tracking-tight  dark:text-white text-gray-900 sm:text-4xl">A smarter way to win in Texas Poker</p>
              <p className="mt-6 text-lg leading-8  dark:text-gray-400 text-gray-600">
                Accelerate your poker skills with this powerful AI tools
              </p>
              <dl className="mt-10 max-w-xl space-y-8 text-base leading-7 text-gray-600 lg:max-w-none">
                {features.map((feature) => (
                  <div key={feature.name} className="relative pl-9">
                    <dt className="inline font-semibold dark:text-gray-100 text-gray-900">
                      <feature.icon className="absolute left-1 top-1 h-5 w-5" aria-hidden="true" />
                      {feature.name}
                    </dt>{' '}
                    <dd className="inline dark:text-gray-400">{feature.description}</dd>
                  </div>
                ))}
              </dl>
            </div>
          </div>
          <OrbitingCirclesComponent />
        </div>
      </div>
    </div>
  )
}