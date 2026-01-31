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
        <!-- Dashboard Overview -->
        <div v-if="currentTab === 'dashboard'">
          <!-- Hero Section -->
          <div class="relative px-8 py-16 overflow-hidden">
            <div class="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-yellow-500/10 to-transparent"></div>
            <div class="relative z-10">
              <div class="text-sm text-yellow-400 font-bold uppercase tracking-widest mb-4">Welcome Back</div>
              <h2 class="text-7xl font-black mb-6 leading-tight">
                <span class="text-white">YOUR</span><br/>
                <span class="text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 via-amber-400 to-orange-400">
                  POWER STATUS
                </span>
              </h2>
              <p class="text-xl text-gray-400 max-w-2xl">
                Real-time monitoring and intelligent optimization for your home energy system
              </p>
            </div>
          </div>

          <!-- Stats Section - Asymmetric Layout -->
          <div class="px-8 pb-12">
            <div class="grid grid-cols-12 gap-6">
              <!-- Large featured stat -->
              <div class="col-span-12 lg:col-span-7 relative overflow-hidden">
                <div class="bg-gradient-to-br from-gray-900/90 to-gray-950/90 rounded-2xl p-10 border-2 border-yellow-500/30 shadow-2xl h-full relative overflow-hidden">
                  <div class="absolute top-0 right-0 w-64 h-64 bg-yellow-500/10 rounded-full blur-3xl"></div>
                  <div class="relative z-10">
                    <div class="flex items-start justify-between mb-8">
                      <div>
                        <div class="text-yellow-400/70 text-sm font-bold uppercase tracking-widest mb-3">Currently Running On</div>
                        <div class="text-6xl font-black text-white mb-2">{{ powerSource }}</div>
                        <div class="text-gray-500 uppercase text-sm font-bold">Power Source</div>
                      </div>
                      <div :class="['text-8xl', powerSource === 'Battery' ? 'drop-shadow-[0_0_20px_rgba(34,197,94,0.7)]' : 'drop-shadow-[0_0_20px_rgba(234,179,8,0.7)]']">
                        {{ powerSource === 'Battery' ? '🔋' : '🔌' }}
                      </div>
                    </div>
                    
                    <!-- Mini stats row -->
                    <div class="grid grid-cols-3 gap-4 pt-6 border-t border-gray-800">
                      <div>
                        <div class="text-gray-500 text-xs uppercase mb-1">Battery</div>
                        <div class="text-2xl font-black text-yellow-400">{{ batteryLevel }}%</div>
                      </div>
                      <div>
                        <div class="text-gray-500 text-xs uppercase mb-1">Price</div>
                        <div class="text-2xl font-black text-amber-400">${{ currentPrice }}</div>
                      </div>
                      <div>
                        <div class="text-gray-500 text-xs uppercase mb-1">Saved</div>
                        <div class="text-2xl font-black text-green-400">${{ todaySavings }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Stacked smaller stats -->
              <div class="col-span-12 lg:col-span-5 flex flex-col gap-6">
                <div class="bg-gradient-to-br from-gray-900/90 to-gray-950/90 rounded-2xl p-8 border-2 border-amber-500/30 shadow-xl relative overflow-hidden">
                  <div class="absolute bottom-0 left-0 w-48 h-48 bg-amber-500/10 rounded-full blur-3xl"></div>
                  <div class="relative z-10">
                    <div class="text-amber-400/70 text-xs font-bold uppercase tracking-widest mb-3">Battery Level</div>
                    <div class="flex items-end gap-2 mb-4">
                      <div class="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-amber-400">
                        {{ batteryLevel }}
                      </div>
                      <div class="text-2xl font-black text-gray-500 mb-1">%</div>
                    </div>
                    <div class="bg-gray-800 rounded-full h-4 overflow-hidden border border-gray-700">
                      <div 
                        class="h-4 rounded-full bg-gradient-to-r from-yellow-500 via-amber-500 to-orange-500 shadow-lg transition-all"
                        :style="{ width: batteryLevel + '%' }"
                      ></div>
                    </div>
                  </div>
                </div>

                <div class="bg-gradient-to-br from-gray-900/90 to-gray-950/90 rounded-2xl p-8 border-2 border-green-500/30 shadow-xl relative overflow-hidden">
                  <div class="absolute top-0 right-0 w-48 h-48 bg-green-500/10 rounded-full blur-3xl"></div>
                  <div class="relative z-10">
                    <div class="text-green-400/70 text-xs font-bold uppercase tracking-widest mb-3">Today's Savings</div>
                    <div class="flex items-end gap-2">
                      <div class="text-5xl font-black text-green-400 drop-shadow-[0_0_15px_rgba(34,197,94,0.5)]">
                        ${{ todaySavings }}
                      </div>
                    </div>
                    <div class="text-gray-500 text-sm mt-2">vs. grid-only operation</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Full-width stats bar -->
          <div class="px-8 pb-12">
            <div class="bg-gradient-to-r from-gray-900/90 via-gray-950/90 to-gray-900/90 rounded-2xl p-8 border-y-2 border-yellow-500/20 relative overflow-hidden">
              <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-yellow-500 via-amber-500 to-orange-500"></div>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div class="flex items-center gap-6 border-l-4 border-yellow-500 pl-6">
                  <div class="text-5xl drop-shadow-[0_0_15px_rgba(234,179,8,0.5)]">⚡</div>
                  <div>
                    <div class="text-yellow-400/70 text-xs font-bold uppercase tracking-widest mb-1">Energy Used Today</div>
                    <div class="text-4xl font-black text-yellow-300">18.4 <span class="text-xl text-gray-500">kWh</span></div>
                  </div>
                </div>
                <div class="flex items-center gap-6 border-l-4 border-amber-500 pl-6">
                  <div class="text-5xl drop-shadow-[0_0_15px_rgba(245,158,11,0.5)]">🔄</div>
                  <div>
                    <div class="text-amber-400/70 text-xs font-bold uppercase tracking-widest mb-1">Battery Cycles</div>
                    <div class="text-4xl font-black text-amber-300">47</div>
                  </div>
                </div>
                <div class="flex items-center gap-6 border-l-4 border-green-500 pl-6">
                  <div class="text-5xl drop-shadow-[0_0_15px_rgba(34,197,94,0.5)]">✓</div>
                  <div>
                    <div class="text-green-400/70 text-xs font-bold uppercase tracking-widest mb-1">System Uptime</div>
                    <div class="text-4xl font-black text-green-300">99.2<span class="text-xl text-gray-500">%</span></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Energy Usage -->
        <div v-if="currentTab === 'energy'">
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
                <div class="text-5xl font-black text-yellow-400 mt-2">18.4 <span class="text-2xl text-gray-500">kWh</span></div>
              </div>
              <div class="bg-gradient-to-br from-amber-900/20 to-amber-950/20 rounded-xl p-6 border-l-4 border-amber-500">
                <div class="text-amber-400/70 text-xs font-bold uppercase tracking-widest">This Week</div>
                <div class="text-5xl font-black text-amber-400 mt-2">124.8 <span class="text-2xl text-gray-500">kWh</span></div>
              </div>
              <div class="bg-gradient-to-br from-orange-900/20 to-orange-950/20 rounded-xl p-6 border-l-4 border-orange-500">
                <div class="text-orange-400/70 text-xs font-bold uppercase tracking-widest">This Month</div>
                <div class="text-5xl font-black text-orange-400 mt-2">487.2 <span class="text-2xl text-gray-500">kWh</span></div>
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

        <!-- Battery & Power -->
        <div v-if="currentTab === 'battery'">
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
                  {{ batteryStatus.toUpperCase() }}
                </div>
              </div>
              <div class="bg-gradient-to-br from-gray-900/90 to-gray-950/90 rounded-xl p-6 border-l-4 border-amber-500">
                <div class="text-gray-400 font-bold uppercase text-sm mb-3">Capacity</div>
                <div class="text-3xl font-black text-amber-400">10 kWh</div>
              </div>
              <div class="bg-gradient-to-br from-gray-900/90 to-gray-950/90 rounded-xl p-6 border-l-4 border-green-500">
                <div class="text-gray-400 font-bold uppercase text-sm mb-3">Health</div>
                <div class="text-3xl font-black text-green-400">98%</div>
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
                <div class="flex items-center gap-6 p-6 bg-gray-800/50 rounded-xl border-l-4 border-green-500 hover:bg-gray-800 transition-all">
                  <div class="text-5xl drop-shadow-[0_0_15px_rgba(34,197,94,0.5)]">🔋</div>
                  <div class="flex-1">
                    <div class="font-black text-xl text-white mb-1">SWITCHED TO BATTERY POWER</div>
                    <div class="text-sm text-gray-500 font-mono">Peak rate detected ($0.28/kWh)</div>
                  </div>
                  <div class="text-sm text-gray-600 font-mono uppercase">2h ago</div>
                </div>
                <div class="flex items-center gap-6 p-6 bg-gray-800/50 rounded-xl border-l-4 border-yellow-500 hover:bg-gray-800 transition-all">
                  <div class="text-5xl drop-shadow-[0_0_15px_rgba(234,179,8,0.5)]">⚡</div>
                  <div class="flex-1">
                    <div class="font-black text-xl text-white mb-1">STARTED BATTERY CHARGING</div>
                    <div class="text-sm text-gray-500 font-mono">Off-peak rate ($0.08/kWh)</div>
                  </div>
                  <div class="text-sm text-gray-600 font-mono uppercase">5h ago</div>
                </div>
                <div class="flex items-center gap-6 p-6 bg-gray-800/50 rounded-xl border-l-4 border-amber-500 hover:bg-gray-800 transition-all">
                  <div class="text-5xl drop-shadow-[0_0_15px_rgba(245,158,11,0.5)]">🔌</div>
                  <div class="flex-1">
                    <div class="font-black text-xl text-white mb-1">SWITCHED TO GRID POWER</div>
                    <div class="text-sm text-gray-500 font-mono">Battery fully charged</div>
                  </div>
                  <div class="text-sm text-gray-600 font-mono uppercase">7h ago</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Cost & Savings -->
        <div v-if="currentTab === 'cost'">
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
                    $28.40
                  </div>
                  <div class="text-gray-500 text-sm mt-2 uppercase">40% Reduction</div>
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
                <div class="text-6xl font-black text-green-400 mb-2">$42.80</div>
                <div class="text-gray-500 uppercase text-sm">Estimated monthly cost</div>
              </div>
              <div class="bg-gradient-to-br from-red-900/20 to-red-950/20 rounded-2xl p-10 border-l-4 border-red-500 relative overflow-hidden">
                <div class="absolute top-4 right-4 text-6xl opacity-20">✗</div>
                <div class="text-red-400/70 text-sm font-bold uppercase tracking-widest mb-3">Without System</div>
                <div class="text-6xl font-black text-red-400 mb-2">$71.20</div>
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
                <div>
                  <div class="flex justify-between items-center mb-4">
                    <div>
                      <div class="text-gray-400 font-bold uppercase text-sm mb-1">Peak Hours (Grid)</div>
                      <div class="text-gray-600 text-xs font-mono">High-cost electricity usage</div>
                    </div>
                    <span class="text-red-400 font-black text-3xl">$18.20</span>
                  </div>
                  <div class="bg-gray-800 rounded-full h-4 overflow-hidden border border-gray-700">
                    <div class="bg-gradient-to-r from-red-600 to-red-500 h-4 rounded-full shadow-lg shadow-red-500/50" style="width: 42%"></div>
                  </div>
                </div>
                <div>
                  <div class="flex justify-between items-center mb-4">
                    <div>
                      <div class="text-gray-400 font-bold uppercase text-sm mb-1">Off-Peak (Battery Charging)</div>
                      <div class="text-gray-600 text-xs font-mono">Low-cost charging windows</div>
                    </div>
                    <span class="text-yellow-400 font-black text-3xl">$12.40</span>
                  </div>
                  <div class="bg-gray-800 rounded-full h-4 overflow-hidden border border-gray-700">
                    <div class="bg-gradient-to-r from-yellow-600 to-yellow-500 h-4 rounded-full shadow-lg shadow-yellow-500/50" style="width: 29%"></div>
                  </div>
                </div>
                <div>
                  <div class="flex justify-between items-center mb-4">
                    <div>
                      <div class="text-gray-400 font-bold uppercase text-sm mb-1">Battery Usage</div>
                      <div class="text-gray-600 text-xs font-mono">Stored energy deployment</div>
                    </div>
                    <span class="text-green-400 font-black text-3xl">$12.20</span>
                  </div>
                  <div class="bg-gray-800 rounded-full h-4 overflow-hidden border border-gray-700">
                    <div class="bg-gradient-to-r from-green-600 to-green-500 h-4 rounded-full shadow-lg shadow-green-500/50" style="width: 29%"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- System Status -->
        <div v-if="currentTab === 'system'">
          <!-- Hero section -->
          <div class="px-8 py-12">
            <div class="text-sm text-yellow-400 font-bold uppercase tracking-widest mb-2">Diagnostics</div>
            <h2 class="text-6xl font-black mb-8">
              <span class="text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-amber-400">
                SYSTEM STATUS
              </span>
            </h2>
          </div>

          <!-- Status grid -->
          <div class="px-8 pb-12">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              <!-- System Status -->
              <div class="bg-gradient-to-br from-gray-900/90 to-gray-950/90 rounded-2xl p-8 border-2 border-yellow-500/20 shadow-2xl relative overflow-hidden">
                <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-yellow-500 to-green-500"></div>
                <h3 class="text-2xl font-black mb-6 text-white uppercase">System Health</h3>
                <div class="space-y-5">
                  <div 
                    v-for="item in systemStatus" 
                    :key="item.label" 
                    class="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg border border-gray-700"
                  >
                    <span class="text-gray-400 font-bold uppercase text-sm">{{ item.label }}</span>
                    <span class="flex items-center gap-3">
                      <span :class="`w-3 h-3 bg-${item.color}-500 rounded-full animate-pulse shadow-lg shadow-${item.color}-500/50`"></span>
                      <span :class="`text-${item.color}-400 font-black uppercase`">{{ item.status }}</span>
                    </span>
                  </div>
                  <div class="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                    <span class="text-gray-400 font-bold uppercase text-sm">Last Update</span>
                    <span class="text-white font-mono">{{ lastUpdate }}</span>
                  </div>
                  <div class="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                    <span class="text-gray-400 font-bold uppercase text-sm">Uptime</span>
                    <span class="text-white font-mono font-black">15d 7h 23m</span>
                  </div>
                </div>
              </div>

              <!-- Device Info -->
              <div class="bg-gradient-to-br from-gray-900/90 to-gray-950/90 rounded-2xl p-8 border-2 border-amber-500/20 shadow-2xl relative overflow-hidden">
                <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-amber-500 to-orange-500"></div>
                <h3 class="text-2xl font-black mb-6 text-white uppercase">Device Info</h3>
                <div class="space-y-5">
                  <div class="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                    <div class="text-gray-500 text-xs uppercase mb-2">Device ID</div>
                    <div class="font-mono text-xl text-yellow-400 font-bold">RPi-4B-A7F2</div>
                  </div>
                  <div class="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                    <div class="text-gray-500 text-xs uppercase mb-2">Firmware</div>
                    <div class="text-white font-mono text-xl font-bold">v1.2.4</div>
                  </div>
                  <div class="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                    <div class="text-gray-500 text-xs uppercase mb-2">IP Address</div>
                    <div class="font-mono text-xl text-amber-400 font-bold">192.168.1.142</div>
                  </div>
                  <div class="grid grid-cols-2 gap-4">
                    <div class="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                      <div class="text-gray-500 text-xs uppercase mb-2">CPU</div>
                      <div class="text-white font-black text-2xl">24%</div>
                    </div>
                    <div class="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                      <div class="text-gray-500 text-xs uppercase mb-2">Memory</div>
                      <div class="text-white font-black text-2xl">1.2/4GB</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Settings - Full width -->
            <div class="bg-gradient-to-br from-gray-900/90 to-gray-950/90 rounded-2xl p-10 border-2 border-orange-500/20 shadow-2xl relative overflow-hidden">
              <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-orange-500 via-amber-500 to-yellow-500"></div>
              <h3 class="text-2xl font-black mb-8 text-white uppercase">Optimization Settings</h3>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div 
                  v-for="setting in settings" 
                  :key="setting.name" 
                  class="p-6 bg-gray-800/50 rounded-xl border border-gray-700 hover:border-yellow-500/50 transition-all"
                >
                  <div class="flex items-start justify-between mb-4">
                    <div class="flex-1">
                      <div class="font-black text-white uppercase text-lg mb-1">{{ setting.name }}</div>
                      <div class="text-sm text-gray-500 font-mono">{{ setting.desc }}</div>
                    </div>
                  </div>
                  <label class="relative inline-flex items-center cursor-pointer w-full">
                    <input type="checkbox" class="sr-only peer" :checked="setting.checked" />
                    <div class="w-full h-12 bg-gray-700 peer-focus:outline-none rounded-lg peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[4px] after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-md after:h-10 after:w-10 after:transition-all peer-checked:bg-gradient-to-r peer-checked:from-yellow-500 peer-checked:to-amber-500 shadow-lg peer-checked:shadow-yellow-500/50"></div>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer spacing -->
      <div class="h-20"></div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SmartHomeDashboard',
  data() {
    return {
      currentTab: 'dashboard',
      powerSource: 'Battery',
      batteryLevel: 78,
      batteryStatus: 'Discharging',
      currentPrice: '0.28',
      priceTier: 'Peak',
      todaySavings: '2.13',
      lastUpdate: '2 mins ago',
      tabs: [
        { id: 'dashboard', name: 'Dashboard', icon: '📊' },
        { id: 'energy', name: 'Energy', icon: '⚡' },
        { id: 'battery', name: 'Battery', icon: '🔋' },
        { id: 'cost', name: 'Cost', icon: '💰' },
        { id: 'system', name: 'System', icon: '⚙️' }
      ],
      hourlyData: Array.from({ length: 24 }, (_, i) => ({
        hour: `${i}:00`,
        usage: (Math.random() * 2 + 0.5).toFixed(2)
      })),
      dailyData: [
        { day: 'Mon', usage: 22.4 },
        { day: 'Tue', usage: 18.9 },
        { day: 'Wed', usage: 24.1 },
        { day: 'Thu', usage: 19.7 },
        { day: 'Fri', usage: 21.3 },
        { day: 'Sat', usage: 16.8 },
        { day: 'Sun', usage: 18.4 }
      ],
      pricingData: Array.from({ length: 24 }, (_, i) => ({
        hour: `${i}:00`,
        price: i >= 0 && i < 6 ? 0.08 : i >= 17 && i < 21 ? 0.28 : 0.15
      })),
      systemStatus: [
        { label: 'System', status: 'Online', color: 'green' },
        { label: 'API Connection', status: 'Connected', color: 'green' },
        { label: 'Raspberry Pi', status: 'Active', color: 'green' }
      ],
      settings: [
        { name: 'Cost Optimization', desc: 'Auto-switch based on pricing', checked: true },
        { name: 'Outage Backup', desc: 'Reserve battery for outages', checked: true },
        { name: 'Smart Scheduling', desc: 'Learn usage patterns', checked: false }
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