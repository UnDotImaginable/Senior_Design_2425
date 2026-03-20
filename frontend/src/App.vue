<template>
  <div class="relative min-h-screen bg-black text-gray-100 overflow-x-hidden">
    <!-- Dark gritty background -->
    <div class="fixed inset-0 bg-gradient-to-br from-gray-950 via-black to-gray-900"></div>

    <!-- Neon glow effects - Yellow/Amber theme -->
    <div class="fixed inset-0 overflow-hidden opacity-40 pointer-events-none">
      <div class="absolute top-0 left-0 w-[600px] h-[600px] bg-yellow-500 rounded-full mix-blend-screen filter blur-[120px] opacity-30"></div>
      <div class="absolute top-1/2 right-0 w-[500px] h-[500px] bg-amber-500 rounded-full mix-blend-screen filter blur-[120px] opacity-30"></div>
      <div class="absolute bottom-0 left-1/3 w-[400px] h-[400px] bg-orange-600 rounded-full mix-blend-screen filter blur-[120px] opacity-30"></div>
    </div>

    <!-- Scanline effect -->
    <div class="fixed inset-0 pointer-events-none opacity-5 bg-repeat" style="background-image: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,255,255,0.03) 2px, rgba(255,255,255,0.03) 4px)"></div>

    <!-- Content -->
    <div class="relative z-10">
      <!-- Top Navigation - Sticky -->
      <div class="sticky top-0 z-50 bg-black/80 backdrop-blur-md border-b border-yellow-500/30 shadow-lg shadow-yellow-500/10">
        <div class="max-w-[1600px] mx-auto px-8 py-4 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <h1 class="text-3xl font-black tracking-tight">
              <span class="text-yellow-400 drop-shadow-[0_0_10px_rgba(234,179,8,0.5)]">⚡ POWER</span>
              <span class="text-amber-400 drop-shadow-[0_0_10px_rgba(245,158,11,0.5)]">OPTIM</span>
            </h1>
          </div>
          <div class="text-xs text-yellow-300/70 font-mono uppercase tracking-widest">
            {{ lastUpdate }}
          </div>
        </div>

        <nav class="max-w-[1600px] mx-auto px-8 flex gap-1 pb-[2px]">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="currentTab = tab.id"
            :class="[
              'px-5 py-2 transition-all flex items-center gap-2 whitespace-nowrap font-bold uppercase text-xs tracking-wide relative',
              currentTab === tab.id ? 'text-yellow-300' : 'text-gray-500 hover:text-gray-300'
            ]"
          >
            <div v-if="currentTab === tab.id" class="absolute bottom-0 left-0 right-0 h-[2px] bg-gradient-to-r from-yellow-400 via-amber-400 to-yellow-400 shadow-lg shadow-yellow-500/50"></div>
            <span class="text-base">{{ tab.icon }}</span>
            <span>{{ tab.name }}</span>
          </button>
        </nav>
      </div>

      <!-- Main Content -->
      <div class="max-w-[1600px] mx-auto">
        <DashboardTab v-if="currentTab === 'dashboard'" />
        <EnergyTab    v-if="currentTab === 'energy'" />
        <BatteryTab   v-if="currentTab === 'battery'" />
        <CostTab      v-if="currentTab === 'cost'" />
        <SystemTab    v-if="currentTab === 'system'" />
      </div>

      <!-- Footer spacing -->
      <div class="h-20"></div>
    </div>
  </div>
</template>

<script>
import DashboardTab from './components/Dashboard.vue'
import EnergyTab    from './components/Energy.vue'
import BatteryTab   from './components/Battery.vue'
import CostTab      from './components/Cost.vue'
import SystemTab    from './components/System.vue'

export default {
  name: 'SmartHomeDashboard',
  components: {
    DashboardTab,
    EnergyTab,
    BatteryTab,
    CostTab,
    SystemTab
  },
  data() {
    return {
      currentTab: 'dashboard',
      lastUpdate: '2 mins ago',
      tabs: [
        { id: 'dashboard', name: 'Dashboard', icon: '📊' },
        { id: 'energy',    name: 'Energy',    icon: '⚡' },
        { id: 'battery',   name: 'Battery',   icon: '🔋' },
        { id: 'cost',      name: 'Cost',      icon: '💰' },
        { id: 'system',    name: 'System',    icon: '⚙️' }
      ]
    }
  }
}
</script>

<style scoped>
/* Custom scrollbar for dark theme */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #1f2937;
}

::-webkit-scrollbar-thumb {
  background: #4b5563;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #6b7280;
}
</style>
