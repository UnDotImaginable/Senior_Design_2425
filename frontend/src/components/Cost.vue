<template>
  <div>
    <!-- Hero Section -->
    <div class="relative px-8 py-16 overflow-hidden">
      <div class="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-green-500/10 to-transparent"></div>
      <div class="relative z-10">
        <div class="text-sm text-green-400 font-bold uppercase tracking-widest mb-4">Savings Overview</div>
        <h2 class="text-7xl font-black mb-6 leading-tight">
          <span class="text-white">PRICE</span><br/>
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-green-400 via-emerald-400 to-yellow-400">
            COMPARISON
          </span>
        </h2>
        <p class="text-xl text-gray-400 max-w-2xl">
          Grid price vs. what you actually paid — last 24 hours
        </p>
      </div>
    </div>

    <!-- Chart -->
    <div class="px-8 pb-12">
      <div class="bg-gradient-to-br from-gray-900/90 to-gray-950/90 rounded-2xl p-10 border-2 border-green-500/20 shadow-2xl relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-red-500 via-yellow-500 to-green-500"></div>

        <div class="flex items-center justify-between mb-8">
          <h3 class="text-2xl font-black text-white uppercase">24-Hour Price Comparison</h3>
          <div class="flex items-center gap-6 text-xs font-bold uppercase text-gray-500">
            <span class="flex items-center gap-2">
              <span class="w-5 h-0.5 bg-red-400 inline-block rounded"></span>Grid Price
            </span>
            <span class="flex items-center gap-2">
              <span class="w-5 h-0.5 bg-green-400 inline-block rounded"></span>Actual Price Paid
            </span>
          </div>
        </div>

        <div class="h-96" v-if="chartData">
          <Line :data="chartData" :options="chartOptions" />
        </div>
        <div v-else class="h-96 flex items-center justify-center text-gray-600 uppercase font-bold tracking-widest">
          Loading...
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler)

export default {
  name: 'CostTab',
  components: { Line },
  data() {
    return {
      chartData: null,
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false,
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#111827',
            borderColor: '#374151',
            borderWidth: 1,
            titleColor: '#9ca3af',
            bodyColor: '#f3f4f6',
            padding: 12,
            callbacks: {
              label(ctx) {
                const val = ctx.parsed.y
                return ` ${ctx.dataset.label}: ${val != null ? '$' + val.toFixed(4) + '/kWh' : 'N/A'}`
              }
            }
          }
        },
        scales: {
          x: {
            ticks: { color: '#6b7280', font: { size: 11 }, maxRotation: 0, maxTicksLimit: 12 },
            grid: { color: '#1f2937' },
            border: { color: '#374151' }
          },
          y: {
            ticks: {
              color: '#6b7280',
              font: { size: 11 },
              callback: val => '$' + val.toFixed(4)
            },
            grid: { color: '#1f2937' },
            border: { color: '#374151' }
          }
        }
      }
    }
  },
  async mounted() {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/api/cost/price-comparison`)
      const data = await res.json()

      this.chartData = {
        labels: data.hours.map(h => {
          const d = new Date(h.hour)
          return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }),
        datasets: [
          {
            label: 'Grid Price',
            data: data.hours.map(h => h.grid_price),
            borderColor: '#f87171',
            backgroundColor: 'rgba(248, 113, 113, 0.06)',
            pointBackgroundColor: '#f87171',
            pointRadius: 3,
            pointHoverRadius: 5,
            borderWidth: 2,
            tension: 0.3,
            fill: false,
          },
          {
            label: 'Actual Price Paid',
            data: data.hours.map(h => h.actual_price),
            borderColor: '#4ade80',
            backgroundColor: 'rgba(74, 222, 128, 0.06)',
            pointBackgroundColor: '#4ade80',
            pointRadius: 3,
            pointHoverRadius: 5,
            borderWidth: 2,
            tension: 0.3,
            fill: false,
          }
        ]
      }
    } catch (err) {
      console.error('Failed to fetch price comparison data:', err)
    }
  }
}
</script>
