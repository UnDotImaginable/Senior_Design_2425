<template>
  <div>
    <!-- Hero-style header -->
    <div class="px-8 py-12">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        <div>
          <div class="text-sm text-yellow-400 font-bold uppercase tracking-widest mb-2">Power Management</div>
          <h2 class="text-6xl font-black mb-6 leading-tight">
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-amber-400">
              BATTERY<br/>& POWER
            </span>
          </h2>
          <p class="text-xl text-gray-400">
            Monitor your battery health, power flow, and system switching history in real-time
          </p>
        </div>
        <div class="flex items-center justify-center">
          <div class="relative">
            <div class="text-[200px] drop-shadow-[0_0_40px_rgba(34,197,94,0.6)]">🔋</div>
            <div class="absolute inset-0 flex items-center justify-center">
              <div class="text-6xl font-black text-white drop-shadow-[0_0_20px_rgba(0,0,0,0.9)]">{{ batteryLevel }}%</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Content sections -->
    <div class="px-8 pb-12">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        <div class="bg-gradient-to-br from-gray-900/90 to-gray-950/90 rounded-xl p-6 border-l-4 border-yellow-500">
          <div class="text-gray-400 font-bold uppercase text-sm mb-3">Status</div>
          <div :class="['text-3xl font-black', batteryStatus === 'Charging' ? 'text-green-400' : 'text-yellow-400']">
            {{ batteryStatus ? batteryStatus.toUpperCase() : '' }}
          </div>
        </div>
        <div class="bg-gradient-to-br from-gray-900/90 to-gray-950/90 rounded-xl p-6 border-l-4 border-amber-500">
          <div class="text-gray-400 font-bold uppercase text-sm mb-3">Capacity</div>
          <div class="text-3xl font-black text-amber-400">{{ batteryCapacity }} kWh</div>
        </div>
        <div class="bg-gradient-to-br from-gray-900/90 to-gray-950/90 rounded-xl p-6 border-l-4 border-green-500">
          <div class="text-gray-400 font-bold uppercase text-sm mb-3">Health</div>
          <div class="text-3xl font-black text-green-400">{{ batteryHealth }}%</div>
        </div>
      </div>

      <!-- Power Flow - Full width -->
      <div class="bg-gradient-to-br from-gray-900/90 to-gray-950/90 rounded-2xl p-12 border-2 border-amber-500/20 shadow-2xl mb-8 relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-amber-500 to-orange-500"></div>
        <h3 class="text-2xl font-black mb-8 text-white uppercase text-center">Power Flow Diagram</h3>
        <div class="flex items-center justify-center gap-16">
          <div class="text-center">
            <div class="text-8xl mb-4 drop-shadow-[0_0_30px_rgba(234,179,8,0.6)]">🔌</div>
            <div class="text-lg text-gray-400 font-bold uppercase">Grid</div>
          </div>
          <div class="text-7xl font-black text-yellow-400 drop-shadow-[0_0_20px_rgba(234,179,8,0.6)]">
            {{ powerSource === 'Grid' ? '→' : '←' }}
          </div>
          <div class="text-center">
            <div class="text-8xl mb-4 drop-shadow-[0_0_30px_rgba(245,158,11,0.6)]">🏠</div>
            <div class="text-lg text-gray-400 font-bold uppercase">Home</div>
          </div>
          <div class="text-7xl font-black text-amber-400 drop-shadow-[0_0_20px_rgba(245,158,11,0.6)]">
            ↕
          </div>
          <div class="text-center">
            <div class="text-8xl mb-4 drop-shadow-[0_0_30px_rgba(34,197,94,0.6)]">🔋</div>
            <div class="text-lg text-gray-400 font-bold uppercase">Battery</div>
          </div>
        </div>
      </div>

      <!-- Activity Log -->
      <div class="bg-gradient-to-br from-gray-900/90 to-gray-950/90 rounded-2xl p-8 border-2 border-orange-500/20 shadow-2xl relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-orange-500 via-amber-500 to-yellow-500"></div>
        <h3 class="text-2xl font-black mb-6 text-white uppercase">Recent Activity</h3>
        <div class="space-y-4">
          <div
            v-for="(item, i) in recentActivity"
            :key="i"
            :class="['flex items-center gap-6 p-6 bg-gray-800/50 rounded-xl border-l-4 hover:bg-gray-800 transition-all', activityBorderColor(item.icon)]"
          >
            <div :class="['text-5xl', activityGlow(item.icon)]">{{ item.icon }}</div>
            <div class="flex-1">
              <div class="font-black text-xl text-white mb-1">{{ item.action }}</div>
              <div class="text-sm text-gray-500 font-mono">{{ item.details }}</div>
            </div>
            <div class="text-sm text-gray-600 font-mono uppercase">{{ item.timestamp }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BatteryTab',
  data() {
    return {
      batteryLevel: null,
      batteryStatus: null,
      batteryCapacity: null,
      batteryHealth: null,
      powerSource: null,
      recentActivity: []
    }
  },
  async mounted() {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/api/battery/`)
      const data = await res.json()
      this.batteryLevel    = data.status.level
      this.batteryStatus   = data.status.status
      this.batteryCapacity = data.status.capacity
      this.batteryHealth   = data.status.health
      this.powerSource     = data.status.status === 'Discharging' ? 'Battery' : 'Grid'
      this.recentActivity  = data.recentActivity
    } catch (err) {
      console.error('Failed to fetch battery data:', err)
    }
  },
  methods: {
    activityBorderColor(icon) {
      if (icon === '🔋') return 'border-green-500'
      if (icon === '⚡') return 'border-yellow-500'
      return 'border-amber-500'
    },
    activityGlow(icon) {
      if (icon === '🔋') return 'drop-shadow-[0_0_15px_rgba(34,197,94,0.5)]'
      if (icon === '⚡') return 'drop-shadow-[0_0_15px_rgba(234,179,8,0.5)]'
      return 'drop-shadow-[0_0_15px_rgba(245,158,11,0.5)]'
    }
  }
}
</script>
