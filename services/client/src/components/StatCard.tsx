import type { LucideIcon } from 'lucide-react'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { cn } from 'cn'

interface StatCardProps {
  label: string
  value: string
  change: number
  icon: LucideIcon
}

function StatCard({ label, value, change, icon: Icon }: StatCardProps) {
  const isPositive = change > 0
  const isNegative = change < 0
  const ChangeIcon = isPositive ? TrendingUp : isNegative ? TrendingDown : Minus

  const changeText = isPositive ? `+${change}%` : isNegative ? `${change}%` : '0%'

  return (
    <Card className="border-border-subtle bg-bg-surface">
      <CardContent className="flex items-center gap-4">
        <div className="rounded-lg bg-accent/10 p-2.5">
          <Icon className="size-5 text-accent" />
        </div>
        <div className="flex-1">
          <p className="text-sm text-gray-400">{label}</p>
          <p className="text-2xl font-semibold text-white">{value}</p>
        </div>
        <Badge
          variant="outline"
          className={cn(
            'gap-1 border-transparent',
            isPositive && 'text-positive',
            isNegative && 'text-negative',
            !isPositive && !isNegative && 'text-gray-400',
          )}
        >
          <ChangeIcon className="size-3" />
          {changeText}
        </Badge>
      </CardContent>
    </Card>
  )
}

export default StatCard
