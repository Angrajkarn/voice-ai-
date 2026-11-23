// Database seed script for AI Voice Calling Platform

import { PrismaClient } from '@prisma/client';
import { encrypt } from '../src/utils';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Starting database seed...');

  // Create demo organization
  const organization = await prisma.organization.upsert({
    where: { slug: 'demo-org' },
    update: {},
    create: {
      name: 'Demo Organization',
      slug: 'demo-org',
      plan: 'PROFESSIONAL',
      settings: {
        timezone: 'Asia/Kolkata',
        defaultLanguage: 'en-IN',
        callingWindowStart: '09:00',
        callingWindowEnd: '18:00',
        maxCallsPerDay: 100,
      },
    },
  });
  console.log('✅ Organization created:', organization.name);

  // Create demo admin user
  const adminUser = await prisma.user.upsert({
    where: { email: 'admin@demo.com' },
    update: {},
    create: {
      email: 'admin@demo.com',
      name: 'Demo Admin',
      role: 'ADMIN',
      isActive: true,
      organizationId: organization.id,
      // Password would be hashed in real app
    },
  });
  console.log('✅ Admin user created:', adminUser.email);

  // Create demo campaign
  const campaign = await prisma.campaign.upsert({
    where: { id: 'demo-campaign-1' },
    update: {},
    create: {
      id: 'demo-campaign-1',
      name: 'Product Launch Campaign',
      description: 'Calling customers about our new product launch',
      purpose: 'Introduce new AI-powered product features and gauge interest',
      aiInstructions: `You are an AI assistant calling on behalf of Demo Organization.

Your goal is to introduce our new AI-powered product and understand if the customer is interested in learning more.

Key guidelines:
1. Always identify yourself as an AI assistant calling on behalf of Demo Organization
2. Be polite, professional, and conversational
3. Listen actively to customer responses
4. Answer questions using the knowledge base provided
5. Never make up pricing, features, or promises
6. If customer asks something not in knowledge base, say you'll have a human follow up
7. Respect customer's time and interest level
8. Handle objections gracefully
9. End calls politely with clear next steps

Supported languages: English, Hindi, Hinglish
Always match the customer's language preference.`,
      openingScript: "Hello, am I speaking with {firstName}? Hi {firstName}, I'm an AI assistant calling on behalf of Demo Organization. Is this a good time to speak for a minute about our new product launch?",
      knowledgeBase: `Product: AI Voice Automation Platform
Features:
- Automated outbound calling with AI agents
- Natural conversation in English, Hindi, Hinglish
- Real-time transcription and analytics
- Google Sheets integration
- Callback scheduling
- CRM integration

Pricing:
- Starter: ₹9,999/month (up to 1,000 calls)
- Professional: ₹24,999/month (up to 5,000 calls)
- Enterprise: Custom pricing

Target audience: Sales teams, customer support, lead generation agencies

Common questions:
- "What does it cost?" -> Refer to pricing above
- "How does it work?" -> AI calls customers, has natural conversations, updates your CRM
- "Can I try it?" -> Yes, we offer a 14-day free trial
- "Is it compliant?" -> Yes, we follow TRAI guidelines and DND regulations`,
      voiceId: 'alloy',
      language: 'en-IN',
      supportedLanguages: ['en-IN', 'hi-IN', 'hinglish'],
      maxCallsPerDay: 100,
      maxRetryAttempts: 3,
      delayBetweenCalls: 30,
      callingWindowStart: '09:00',
      callingWindowEnd: '18:00',
      callingTimezone: 'Asia/Kolkata',
      skipWeekends: true,
      allowCallbacks: true,
      callbackWindowStart: '09:00',
      callbackWindowEnd: '18:00',
      maxCallbackDays: 7,
      sheetsSyncEnabled: false,
      sheetsSheetName: 'Calls',
      sheetsAutoSync: true,
      status: 'DRAFT',
      organizationId: organization.id,
      ownerId: adminUser.id,
    },
  });
  console.log('✅ Campaign created:', campaign.name);

  // Create demo customers
  const customersData = [
    {
      firstName: 'Rahul',
      lastName: 'Sharma',
      email: 'rahul.sharma@example.com',
      phone: '+919876543210',
      company: 'TechCorp Solutions',
      location: 'Bangalore',
      language: 'en-IN',
    },
    {
      firstName: 'Priya',
      lastName: 'Patel',
      email: 'priya.patel@example.com',
      phone: '+919876543211',
      company: 'InnovateLabs',
      location: 'Mumbai',
      language: 'hinglish',
    },
    {
      firstName: 'Amit',
      lastName: 'Kumar',
      email: 'amit.kumar@example.com',
      phone: '+919876543212',
      company: 'DataDriven Inc',
      location: 'Delhi',
      language: 'hi-IN',
    },
    {
      firstName: 'Sneha',
      lastName: 'Reddy',
      email: 'sneha.reddy@example.com',
      phone: '+919876543213',
      company: 'CloudScale',
      location: 'Hyderabad',
      language: 'en-IN',
    },
    {
      firstName: 'Vikram',
      lastName: 'Singh',
      email: 'vikram.singh@example.com',
      phone: '+919876543214',
      company: 'GrowthHub',
      location: 'Pune',
      language: 'hinglish',
    },
  ];

  for (const customerData of customersData) {
    const customer = await prisma.customer.upsert({
      where: {
        organizationId_phone: {
          organizationId: organization.id,
          phone: customerData.phone,
        },
      },
      update: {},
      create: {
        ...customerData,
        organizationId: organization.id,
        status: 'NEW',
        interestLevel: 'UNKNOWN',
        maxCallAttempts: 3,
      },
    });

    // Link to campaign
    await prisma.campaignCustomer.upsert({
      where: {
        campaignId_customerId: {
          campaignId: campaign.id,
          customerId: customer.id,
        },
      },
      update: {},
      create: {
        campaignId: campaign.id,
        customerId: customer.id,
        priority: 0,
        status: 'NEW',
      },
    });

    console.log('✅ Customer created:', `${customer.firstName} ${customer.lastName}`);
  }

  // Create Twilio integration (placeholder config)
  await prisma.integration.upsert({
    where: {
      organizationId_type_name: {
        organizationId: organization.id,
        type: 'TWILIO',
        name: 'Primary Twilio Account',
      },
    },
    update: {},
    create: {
      type: 'TWILIO',
      name: 'Primary Twilio Account',
      config: encrypt(JSON.stringify({
        accountSid: 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        authToken: 'your_auth_token_here',
        phoneNumber: '+15551234567',
      })),
      isActive: false, // Not connected until configured
      organizationId: organization.id,
    },
  });
  console.log('✅ Twilio integration created (not configured)');

  // Create OpenAI integration (placeholder config)
  await prisma.integration.upsert({
    where: {
      organizationId_type_name: {
        organizationId: organization.id,
        type: 'OPENAI',
        name: 'OpenAI API',
      },
    },
    update: {},
    create: {
      type: 'OPENAI',
      name: 'OpenAI API',
      config: encrypt(JSON.stringify({
        apiKey: 'sk-xxxxxxxxxxxxxxxxxxxxxxxx',
        model: 'gpt-4o',
        realtimeModel: 'gpt-4o-realtime-preview',
        ttsModel: 'tts-1',
        ttsVoice: 'alloy',
      })),
      isActive: false,
      organizationId: organization.id,
    },
  });
  console.log('✅ OpenAI integration created (not configured)');

  console.log('\n🎉 Database seed completed successfully!');
  console.log('\nDemo credentials:');
  console.log('  Email: admin@demo.com');
  console.log('  Organization: demo-org');
  console.log('\nNext steps:');
  console.log('  1. Configure Twilio credentials in Settings > Integrations');
  console.log('  2. Configure OpenAI API key in Settings > Integrations');
  console.log('  3. Connect Google Sheets for auto-sync');
  console.log('  4. Start the campaign from Campaign Management');
}

main()
  .catch((e) => {
    console.error('❌ Seed failed:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });