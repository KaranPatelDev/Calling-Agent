<template>
  <div class="min-h-screen bg-white">
    <!-- Nav -->
    <nav class="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-xl border-b border-gray-100">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 bg-gradient-to-br from-brand-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Phone :size="16" class="text-white" />
            </div>
            <span class="text-lg font-bold gradient-text">Calling Agent</span>
          </div>
          <div class="hidden md:flex items-center gap-8">
            <a href="#features" class="text-sm text-gray-600 hover:text-gray-900 transition-colors">Features</a>
            <a href="#how-it-works" class="text-sm text-gray-600 hover:text-gray-900 transition-colors">How It Works</a>
            <a href="#pricing" class="text-sm text-gray-600 hover:text-gray-900 transition-colors">Pricing</a>
          </div>
          <div class="flex items-center gap-3">
            <router-link to="/login" class="btn-ghost text-sm">Sign In</router-link>
            <router-link to="/register" class="btn-primary text-sm">Get Started Free</router-link>
          </div>
        </div>
      </div>
    </nav>

    <!-- Hero -->
    <section class="pt-32 pb-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
      <div class="max-w-7xl mx-auto text-center">
        <motion.div
          initial="{ opacity: 0, y: 30 }"
          animate="{ opacity: 1, y: 0 }"
          transition="{ duration: 0.6 }"
        >
          <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-brand-50 text-brand-700 text-sm font-medium mb-8">
            <Sparkles :size="16" />
            AI-Powered Calling Platform
          </div>
          <h1 class="text-5xl md:text-7xl font-bold text-gray-900 tracking-tight mb-6 text-balance">
            Automate Your
            <span class="gradient-text">Outbound Calls</span>
            <br />at Scale
          </h1>
          <p class="text-xl text-gray-600 max-w-2xl mx-auto mb-10 text-balance">
            Create intelligent call scripts, manage contact lists, and launch campaigns — all from one platform. TRAI compliant, multi-language support.
          </p>
        </motion.div>

        <motion.div
          initial="{ opacity: 0, y: 20 }"
          animate="{ opacity: 1, y: 0 }"
          transition="{ duration: 0.6, delay: 0.2 }"
          class="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <router-link to="/register" class="btn-primary text-base px-8 py-3 flex items-center gap-2">
            Start Free Trial
            <ArrowRight :size="18" />
          </router-link>
          <a href="#how-it-works" class="btn-secondary text-base px-8 py-3 flex items-center gap-2">
            <Play :size="18" />
            See How It Works
          </a>
        </motion.div>

        <!-- Hero visual -->
        <motion.div
          initial="{ opacity: 0, y: 40 }"
          animate="{ opacity: 1, y: 0 }"
          transition="{ duration: 0.8, delay: 0.4 }"
          class="mt-16 relative"
        >
          <div class="bg-gradient-to-b from-brand-50/50 to-transparent rounded-3xl p-8 border border-gray-100">
            <div class="bg-white rounded-2xl shadow-glass-lg border border-gray-100 overflow-hidden">
              <div class="flex items-center gap-2 px-4 py-3 bg-gray-50 border-b border-gray-100">
                <div class="flex gap-1.5">
                  <div class="w-3 h-3 rounded-full bg-red-400"></div>
                  <div class="w-3 h-3 rounded-full bg-yellow-400"></div>
                  <div class="w-3 h-3 rounded-full bg-green-400"></div>
                </div>
                <div class="flex-1 text-center text-xs text-gray-400">Calling Agent Dashboard</div>
              </div>
              <div class="p-6 grid grid-cols-2 md:grid-cols-4 gap-4">
                <div v-for="stat in heroStats" :key="stat.label" class="text-left p-4 rounded-xl bg-gray-50">
                  <p class="text-xs text-gray-500">{{ stat.label }}</p>
                  <p class="text-2xl font-bold" :class="stat.color">{{ stat.value }}</p>
                </div>
              </div>
              <div class="px-6 pb-6">
                <div class="bg-gray-50 rounded-xl p-4">
                  <div class="flex items-center gap-3 mb-3">
                    <div class="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center">
                      <PhoneCall :size="14" class="text-emerald-600" />
                    </div>
                    <div>
                      <p class="text-sm font-medium">Mumbai Welcome Campaign</p>
                      <p class="text-xs text-gray-500">5 contacts • Running</p>
                    </div>
                    <span class="badge-success ml-auto">Active</span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div class="bg-emerald-500 h-2 rounded-full" style="width: 60%"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>

    <!-- Features -->
    <section id="features" class="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50/50">
      <div class="max-w-7xl mx-auto">
        <motion.div
          initial="{ opacity: 0, y: 20 }"
          whileInView="{ opacity: 1, y: 0 }"
          viewport="{ once: true }"
          transition="{ duration: 0.5 }"
          class="text-center mb-16"
        >
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Everything You Need</h2>
          <p class="text-lg text-gray-600 max-w-2xl mx-auto">Powerful features to automate and scale your outbound calling operations.</p>
        </motion.div>

        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <motion.div
            v-for="(feature, idx) in features"
            :key="feature.title"
            initial="{ opacity: 0, y: 20 }"
            whileInView="{ opacity: 1, y: 0 }"
            viewport="{ once: true }"
            transition="{ duration: 0.4, delay: idx * 0.1 }"
            class="card-hover group"
          >
            <div class="w-12 h-12 rounded-xl flex items-center justify-center mb-4 transition-transform duration-300 group-hover:scale-110" :class="feature.bgClass">
              <component :is="feature.icon" :size="24" :class="feature.iconClass" />
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ feature.title }}</h3>
            <p class="text-sm text-gray-600 leading-relaxed">{{ feature.description }}</p>
          </motion.div>
        </div>
      </div>
    </section>

    <!-- How It Works -->
    <section id="how-it-works" class="py-20 px-4 sm:px-6 lg:px-8">
      <div class="max-w-7xl mx-auto">
        <motion.div
          initial="{ opacity: 0, y: 20 }"
          whileInView="{ opacity: 1, y: 0 }"
          viewport="{ once: true }"
          transition="{ duration: 0.5 }"
          class="text-center mb-16"
        >
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">How It Works</h2>
          <p class="text-lg text-gray-600 max-w-2xl mx-auto">Get started in three simple steps.</p>
        </motion.div>

        <div class="grid md:grid-cols-3 gap-8">
          <motion.div
            v-for="(step, idx) in steps"
            :key="step.title"
            initial="{ opacity: 0, y: 20 }"
            whileInView="{ opacity: 1, y: 0 }"
            viewport="{ once: true }"
            transition="{ duration: 0.4, delay: idx * 0.15 }"
            class="text-center"
          >
            <div class="w-16 h-16 rounded-2xl bg-gradient-to-br mx-auto mb-6 flex items-center justify-center text-white text-2xl font-bold" :class="step.gradient">
              {{ idx + 1 }}
            </div>
            <h3 class="text-xl font-semibold text-gray-900 mb-3">{{ step.title }}</h3>
            <p class="text-gray-600">{{ step.description }}</p>
          </motion.div>
        </div>
      </div>
    </section>

    <!-- Pricing -->
    <section id="pricing" class="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50/50">
      <div class="max-w-7xl mx-auto">
        <motion.div
          initial="{ opacity: 0, y: 20 }"
          whileInView="{ opacity: 1, y: 0 }"
          viewport="{ once: true }"
          transition="{ duration: 0.5 }"
          class="text-center mb-16"
        >
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Simple Pricing</h2>
          <p class="text-lg text-gray-600 max-w-2xl mx-auto">Start free, scale as you grow.</p>
        </motion.div>

        <div class="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <motion.div
            v-for="(plan, idx) in plans"
            :key="plan.name"
            initial="{ opacity: 0, y: 20 }"
            whileInView="{ opacity: 1, y: 0 }"
            viewport="{ once: true }"
            transition="{ duration: 0.4, delay: idx * 0.1 }"
            class="card-hover relative"
            :class="{ 'ring-2 ring-brand-500 shadow-glow': plan.popular }"
          >
            <div v-if="plan.popular" class="absolute -top-3 left-1/2 -translate-x-1/2 badge-info">Most Popular</div>
            <h3 class="text-xl font-bold text-gray-900 mb-2">{{ plan.name }}</h3>
            <p class="text-sm text-gray-500 mb-4">{{ plan.description }}</p>
            <div class="mb-6">
              <span class="text-4xl font-bold text-gray-900">{{ plan.price }}</span>
              <span v-if="plan.period" class="text-gray-500 text-sm">/{{ plan.period }}</span>
            </div>
            <ul class="space-y-3 mb-8">
              <li v-for="feature in plan.features" :key="feature" class="flex items-center gap-2 text-sm text-gray-600">
                <Check :size="16" class="text-emerald-500 shrink-0" />
                {{ feature }}
              </li>
            </ul>
            <router-link
              to="/register"
              class="block text-center py-2.5 rounded-xl font-medium transition-all duration-200"
              :class="plan.popular ? 'btn-primary w-full' : 'btn-secondary w-full'"
            >
              {{ plan.cta }}
            </router-link>
          </motion.div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="py-20 px-4 sm:px-6 lg:px-8">
      <div class="max-w-4xl mx-auto text-center">
        <motion.div
          initial="{ opacity: 0, y: 20 }"
          whileInView="{ opacity: 1, y: 0 }"
          viewport="{ once: true }"
          transition="{ duration: 0.5 }"
        >
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Ready to Get Started?</h2>
          <p class="text-lg text-gray-600 mb-8 max-w-xl mx-auto">Join hundreds of businesses automating their outbound calls. Free to start, no credit card required.</p>
          <router-link to="/register" class="btn-primary text-base px-10 py-3 inline-flex items-center gap-2">
            Start Free Today
            <ArrowRight :size="18" />
          </router-link>
        </motion.div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="border-t border-gray-100 py-8 px-4 sm:px-6 lg:px-8">
      <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <div class="flex items-center gap-2">
          <div class="w-6 h-6 bg-gradient-to-br from-brand-500 to-purple-600 rounded-md flex items-center justify-center">
            <Phone :size="12" class="text-white" />
          </div>
          <span class="text-sm font-semibold gradient-text">Calling Agent</span>
        </div>
        <p class="text-sm text-gray-500">&copy; {{ new Date().getFullYear() }} Calling Agent. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { motion } from 'motion-v'
import { Phone, ArrowRight, Play, Sparkles, PhoneCall, FileText, Users, BarChart3, Shield, Globe, Zap, Check } from '@lucide/vue'

const heroStats = [
  { label: 'Total Campaigns', value: '12', color: 'text-brand-600' },
  { label: 'Active Campaigns', value: '3', color: 'text-emerald-600' },
  { label: 'Total Calls', value: '1,247', color: 'text-purple-600' },
  { label: 'Success Rate', value: '89%', color: 'text-emerald-600' },
]

const features = [
  { title: 'Smart Scripts', description: 'Create call scripts with TTS or upload pre-recorded audio. Support for 6 Indian languages.', icon: FileText, bgClass: 'bg-blue-100', iconClass: 'text-blue-600' },
  { title: 'Contact Management', description: 'Import contacts from CSV, Excel, or PDF. Validate phone numbers automatically.', icon: Users, bgClass: 'bg-purple-100', iconClass: 'text-purple-600' },
  { title: 'Campaign Automation', description: 'Schedule campaigns with retry logic, calling hours, and concurrent call limits.', icon: PhoneCall, bgClass: 'bg-emerald-100', iconClass: 'text-emerald-600' },
  { title: 'Real-time Analytics', description: 'Track call success rates, campaign progress, and detailed call logs.', icon: BarChart3, bgClass: 'bg-amber-100', iconClass: 'text-amber-600' },
  { title: 'TRAI Compliance', description: 'Built-in DND checking and TRAI regulation compliance for India market.', icon: Shield, bgClass: 'bg-red-100', iconClass: 'text-red-600' },
  { title: 'Multi-language TTS', description: 'Generate speech in Hindi, English, Tamil, Telugu, Bengali, and Marathi.', icon: Globe, bgClass: 'bg-cyan-100', iconClass: 'text-cyan-600' },
]

const steps = [
  { title: 'Create Scripts', description: 'Write your call script or upload pre-recorded audio files. Variables like {customer_name} are supported.', gradient: 'from-brand-500 to-brand-600' },
  { title: 'Add Contacts', description: 'Import your contact list from Excel, CSV, or PDF. We auto-validate Indian phone numbers.', gradient: 'from-purple-500 to-purple-600' },
  { title: 'Launch Campaign', description: 'Set schedule, calling hours, and retry rules. Your campaign starts making calls automatically.', gradient: 'from-emerald-500 to-emerald-600' },
]

const plans = [
  { name: 'Free', description: 'Perfect for trying out', price: '₹0', period: null, cta: 'Get Started', popular: false, features: ['100 calls/month', '1 script', '1 contact list', 'Basic analytics', 'Email support'] },
  { name: 'Pro', description: 'For growing businesses', price: '₹999', period: 'month', cta: 'Start Pro Trial', popular: true, features: ['5,000 calls/month', 'Unlimited scripts', 'Unlimited contacts', 'Advanced analytics', 'Priority support', 'API access'] },
  { name: 'Enterprise', description: 'For large operations', price: 'Custom', period: null, cta: 'Contact Sales', popular: false, features: ['Unlimited calls', 'Unlimited everything', 'Custom integrations', 'Dedicated support', 'SLA guarantee', 'On-premise option'] },
]
</script>
