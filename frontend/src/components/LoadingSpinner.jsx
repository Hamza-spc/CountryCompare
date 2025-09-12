import React from 'react'
import { Loader2 } from 'lucide-react'

function LoadingSpinner({ size = 'md', text = 'Loading...' }) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
    xl: 'h-16 w-16'
  }

  return (
    <div className="flex flex-col items-center justify-center space-y-4 py-8">
      <Loader2 className={`${sizeClasses[size]} animate-spin text-primary-500`} />
      <p className="text-dark-400 text-sm">{text}</p>
    </div>
  )
}

export default LoadingSpinner
