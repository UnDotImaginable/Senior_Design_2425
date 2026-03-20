<template>
  <div>
    <!-- Section Header -->
    <div class="px-8 py-12">
      <div class="text-sm text-yellow-400 font-bold uppercase tracking-widest mb-2">Analytics</div>
      <h2 class="text-6xl font-black mb-4">
        <span class="text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-amber-400">
          ENERGY USAGE
        </span>
      </h2>
    </div>

    <!-- Top stats row -->
    <div class="px-8 pb-8">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-gradient-to-br from-yellow-900/20 to-yellow-950/20 rounded-xl p-6 border-l-4 border-yellow-500">
          <div class="text-yellow-400/70 text-xs font-bold uppercase tracking-widest">Today</div>
          <div class="text-5xl font-black text-yellow-400 mt-2">{{ summaryToday }} <span class="text-2xl text-gray-500">kWh</span></div>
        </div>
        <div class="bg-gradient-to-br from-amber-900/20 to-amber-950/20 rounded-xl p-6 border-l-4 border-amber-500">
          <div class="text-amber-400/70 text-xs font-bold uppercase tracking-widest">This Week</div>
          <div class="text-5xl font-black text-amber-400 mt-2">{{ summaryWeek }} <span class="text-2xl text-gray-500">kWh</span></div>
        </div>
        <div class="bg-gradient-to-br from-orange-900/20 to-orange-950/20 rounded-xl p-6 border-l-4 border-orange-500">
          <div class="text-orange-400/70 text-xs font-bold uppercase tracking-widest">This Month</div>
          <div class="text-5xl font-black text-orange-400 mt-2">{{ summaryMonth }} <span class="text-2xl text-gray-500">kWh</span></div>
        </div>
      </div>
    </div>

    <!-- Charts side by side -->
    <div class="px-8 pb-12">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Hourly Chart -->
        <div class="bg-gradient-to-br from-gray-900/90 to-gray-950/90 rounded-2xl p-8 border-2 border-yellow-500/20 shadow-2xl relative overflow-hidden">
          <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-yellow-500 to-amber-500"></div>
          <h3 class="text-xl font-black mb-6 text-white uppercase">24-Hour Usage</h3>
          <div class="h-72 flex items-end gap-1">
            <div
              v-for="(item, i) in hourlyData"
              :key="i"
              class="flex-1 flex flex-col items-center group"
            >
              <div
                class="w-full bg-gradient-to-t from-yellow-500 via-yellow-400 to-amber-400 rounded-t transition-all shadow-lg shadow-yellow-500/30 hover:shadow-yellow-500/60"
                :style="{ height: (parseFloat(item.usage) / 3) * 100 + '%' }"
                :title="`${item.hour}: ${item.usage} kWh`"
              ></div>
            </div>
          </div>
          <div class="flex justify-between text-xs text-gray-600 mt-4 font-mono">
            <span>00:00</span>
            <span>12:00</span>
            <span>23:00</span>
          </div>
        </div>

        <!-- Daily Chart -->
        <div class="bg-gradient-to-br from-gray-900/90 to-gray-950/90 rounded-2xl p-8 border-2 border-amber-500/20 shadow-2xl relative overflow-hidden">
          <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-amber-500 to-orange-500"></div>
          <h3 class="text-xl font-black mb-6 text-white uppercase">Weekly Usage</h3>
          <div class="h-72 flex items-end gap-4">
            <div
              v-for="(item, i) in dailyData"
              :key="i"
              class="flex-1 flex flex-col items-center gap-3 group"
            >
              <div
                class="w-full bg-gradient-to-t from-amber-600 via-amber-500 to-orange-500 rounded-t transition-all shadow-lg shadow-amber-500/30 hover:shadow-amber-500/60"
                :style="{ height: (item.usage / 25) * 100 + '%' }"
                :title="`${item.day}: ${item.usage} kWh`"
              ></div>
              <span class="text-xs text-gray-500 font-bold uppercase">{{ item.day }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EnergyTab',
  data() {
    return {
      summaryToday: null,
      summaryWeek: null,
      summaryMonth: null,
      hourlyData: [],
      dailyData: []
    }
  },
  async mounted() {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/api/energy/`)
      const data = await res.json()
      this.summaryToday  = data.summary.today
      this.summaryWeek   = data.summary.week
      this.summaryMonth  = data.summary.month
      this.hourlyData    = data.hourlyUsage
      this.dailyData     = data.weeklyUsage
    } catch (err) {
      console.error('Failed to fetch energy data:', err)
    }
  }
}
</script>
