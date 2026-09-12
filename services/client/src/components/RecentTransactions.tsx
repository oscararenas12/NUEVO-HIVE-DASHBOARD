import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Table, TableHeader, TableBody, TableHead, TableRow, TableCell } from '@/components/ui/table'
import type { Transaction } from '@/api/dashboard'

interface RecentTransactionsProps {
  transactions: Transaction[]
  className?: string
}

function formatDate(iso: string) {
  const d = new Date(iso)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) +
    ' ' + d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
}

function RecentTransactions({ transactions, className }: RecentTransactionsProps) {
  return (
    <Card className={`border-border-subtle bg-bg-surface ${className ?? ''}`}>
      <CardHeader>
        <CardTitle className="text-white">Recent Transactions</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow className="border-border-subtle">
              <TableHead className="text-gray-400">Date</TableHead>
              <TableHead className="text-gray-400">Device</TableHead>
              <TableHead className="text-gray-400">Slot</TableHead>
              <TableHead className="text-gray-400">Amount</TableHead>
              <TableHead className="text-gray-400">Payment</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {transactions.map((tx) => (
              <TableRow key={tx.item_ref} className="border-border-subtle">
                <TableCell className="text-gray-300">{formatDate(tx.item_date)}</TableCell>
                <TableCell className="font-mono text-xs text-gray-400">{tx.device}</TableCell>
                <TableCell className="font-mono text-accent">{tx.slot_code}</TableCell>
                <TableCell className="text-white">${tx.amount.toFixed(2)}</TableCell>
                <TableCell className="text-gray-300">{tx.payment_type}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}

export default RecentTransactions
