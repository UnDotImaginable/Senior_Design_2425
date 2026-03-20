<template>
  <div>
    <!-- Split hero section -->
    <div class="px-8 py-12">
      <div class="grid grid-cols-1 lg:grid-cols-5 gap-8 items-end">
        <div class="lg:col-span-3">
          <div class="text-sm text-green-400 font-bold uppercase tracking-widest mb-2">Financial Impact</div>
          <h2 class="text-7xl font-black mb-6 leading-tight">
            <span class="text-white">YOU'RE</span><br/>
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-yellow-400">
              SAVING MONEY
            </span>
          </h2>
        </div>
        <div class="lg:col-span-2">
          <div class="bg-gradient-to-br from-green-900/30 to-green-950/30 rounded-2xl p-8 border-2 border-green-500/50">
            <div class="text-green-400/70 text-xs font-bold uppercase tracking-widest mb-2">This Month</div>
            <div class="text-6xl font-black text-green-400 drop-shadow-[0_0_20px_rgba(34,197,94,0.5)]">
              ${{ monthlyCost?.savings?.toFixed(2) }}
            </div>
            <div class="text-gray-500 text-sm mt-2 uppercase">{{ monthlyCost?.savingsPercentage }}% Reduction</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Comparison cards -->
    <div class="px-8 pb-8">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div class="bg-gradient-to-br from-green-900/20 to-green-950/20 rounded-2xl p-10 border-l-4 border-green-500 relative overflow-hidden">
          <div class="absolute top-4 right-4 text-6xl opacity-20">✓</div>
          <div class="text-green-400/70 text-sm font-bold uppercase tracking-widest mb-3">With PowerOptim</div>
          <div class="text-6xl font-black text-green-400 mb-2">${{ monthlyCost?.withSystem?.toFixed(2) }}</div>
          <div class="text-gray-500 uppercase text-sm">Estimated monthly cost</div>
        </div>
        <div class="bg-gradient-to-br from-red-900/20 to-red-950/20 rounded-2xl p-10 border-l-4 border-red-500 relative overflow-hidden">
          <div class="absolute top-4 right-4 text-6xl opacity-20">✗</div>
          <div class="text-red-400/70 text-sm font-bold uppercase tracking-widest mb-3">Without System</div>
          <div class="text-6xl font-black text-red-400 mb-2">${{ monthlyCost?.withoutSystem?.toFixed(2) }}</div>
          <div class="text-gray-500 uppercase text-sm">Grid-only estimate</div>
        </div>
      </div>
    </div>

    <!-- Pricing Chart - Full width -->
    <div class="px-8 pb-8">
      <div class="bg-gradient-to-br from-gray-900/90 to-gray-950/90 rounded-2xl p-10 border-2 border-yellow-500/20 shadow-2xl relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-red-500 via-yellow-500 to-green-500"></div>
        <h3 class="text-2xl font-black mb-8 text-white uppercase">Today's Pricing Zones</h3>
        <div class="h-80 flex items-end gap-1">
          <div
            v-for="(item, i) in pricingData"
            :key="i"
            class="flex-1 flex flex-col items-center"
          >
            <div
              :class="[
                'w-full rounded-t transition-all shadow-lg',
                item.price === 0.28 ? 'bg-gradient-to-t from-red-600 to-red-500 shadow-red-500/50 hover:shadow-red-500/70' :
                item.price === 0.08 ? 'bg-gradient-to-t from-green-600 to-green-500 shadow-green-500/50 hover:shadow-green-500/70' :
                'bg-gradient-to-t from-yellow-600 to-yellow-500 shadow-yellow-500/50 hover:shadow-yellow-500/70'
              ]"
              :style="{ height: (item.price / 0.3) * 100 + '%' }"
              :title="`${item.hour}: $${item.price}/kWh`"
            ></div>
          </div>
        </div>
        <div class="flex justify-between text-sm text-gray-600 mt-6 font-mono">
          <span>MIDNIGHT</span>
          <span>NOON</span>
          <span>MIDNIGHT</span>
        </div>
      </div>
    </div>

    <!-- Breakdown -->
    <div class="px-8 pb-12">
      <div class="bg-gradient-to-br from-gray-900/90 to-gray-950/90 rounded-2xl p-10 border-2 border-amber-500/20 shadow-2xl relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-red-500 via-yellow-500 to-green-500"></div>
        <h3 class="text-2xl font-black mb-8 text-white uppercase">Cost Breakdown</h3>
        <div class="space-y-8">
          <!-- Peak Hours -->
          <div>
            <div class="flex justify-between items-center mb-4">
              <div>
                <div class="text-gray-400 font-bold uppercase text-sm mb-1">{{ breakdown[0]?.category }}</div>
                <div class="text-gray-600 text-xs font-mono">{{ breakdown[0]?.description }}</div>
              </div>
              <span class="text-red-400 font-black text-3xl">${{ breakdown[0]?.cost?.toFixed(2) }}</span>
            </div>
            <div class="bg-gray-800 rounded-full h-4 overflow-hidden border border-gray-700">
              <div class="bg-gradient-to-r from-red-600 to-red-500 h-4 rounded-full shadow-lg shadow-red-500/50" :style="{ width: (breakdown[0]?.percentage || 0) + '%' }"></div>
            </div>
          </div>
          <!-- Off-Peak -->
          <div>
            <div class="flex justify-between items-center mb-4">
              <div>
                <div class="text-gray-400 font-bold uppercase text-sm mb-1">{{ breakdown[1]?.category }}</div>
                <div class="text-gray-600 text-xs font-mono">{{ breakdown[1]?.description }}</div>
              </div>
              <span class="text-yellow-400 font-black text-3xl">${{ breakdown[1]?.cost?.toFixed(2) }}</span>
            </div>
            <div class="bg-gray-800 rounded-full h-4 overflow-hidden border border-gray-700">
              <div class="bg-gradient-to-r from-yellow-600 to-yellow-500 h-4 rounded-full shadow-lg shadow-yellow-500/50" :style="{ width: (breakdown[1]?.percentage || 0) + '%' }"></div>
            </div>
          </div>
          <!-- Battery Usage -->
          <div>
            <div class="flex justify-between items-center mb-4">
              <div>
                <div class="text-gray-400 font-bold uppercase text-sm mb-1">{{ breakdown[2]?.category }}</div>
                <div class="text-gray-600 text-xs font-mono">{{ breakdown[2]?.description }}</div>
              </div>
              <span class="text-green-400 font-black text-3xl">${{ breakdown[2]?.cost?.toFixed(2) }}</span>
            </div>
            <div class="bg-gray-800 rounded-full h-4 overflow-hidden border border-gray-700">
              <div class="bg-gradient-to-r from-green-600 to-green-500 h-4 rounded-full shadow-lg shadow-green-500/50" :style="{ width: (breakdown[2]?.percentage || 0) + '%' }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CostTab',
  data() {
    return {
      monthlyCost: null,
      pricingData: [],
      breakdown: []
    }
  },
  async mounted() {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/api/cost/`)
      const data = await res.json()
      this.monthlyCost = data.monthlyCost
      this.pricingData = data.pricingZones
      this.breakdown   = data.breakdown
    } catch (err) {
      console.error('Failed to fetch cost data:', err)
    }
  }
}
</script>
