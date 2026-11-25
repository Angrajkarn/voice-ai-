// Campaign API routes

import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@voice-platform/shared/db';
import { createCampaignSchema, updateCampaignSchema, paginationSchema, campaignFiltersSchema } from '@voice-platform/shared/schemas';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';

// GET /api/campaigns - List campaigns
export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.organizationId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const params = {
      page: parseInt(searchParams.get('page') || '1'),
      pageSize: parseInt(searchParams.get('pageSize') || '20'),
      status: searchParams.get('status') || undefined,
      search: searchParams.get('search') || undefined,
      sortBy: searchParams.get('sortBy') || 'createdAt',
      sortOrder: (searchParams.get('sortOrder') as 'asc' | 'desc') || 'desc',
    };

    const validatedParams = paginationSchema.merge(campaignFiltersSchema).parse(params);

    const where: Record<string, unknown> = {
      organizationId: session.user.organizationId,
    };

    if (validatedParams.status) {
      where.status = validatedParams.status;
    }

    if (validatedParams.search) {
      where.OR = [
        { name: { contains: validatedParams.search, mode: 'insensitive' } },
        { description: { contains: validatedParams.search, mode: 'insensitive' } },
      ];
    }

    const sortBy = validatedParams.sortBy === 'name' || validatedParams.sortBy === 'status'
      ? validatedParams.sortBy
      : 'createdAt';

    const [campaigns, total] = await Promise.all([
      prisma.campaign.findMany({
        where,
        orderBy: { [sortBy]: validatedParams.sortOrder },
        skip: (validatedParams.page - 1) * validatedParams.pageSize,
        take: validatedParams.pageSize,
        include: {
          owner: { select: { id: true, name: true, email: true } },
          _count: { select: { campaignCustomers: true, calls: true } },
        },
      }),
      prisma.campaign.count({ where }),
    ]);

    return NextResponse.json({
      data: campaigns,
      total,
      page: validatedParams.page,
      pageSize: validatedParams.pageSize,
      totalPages: Math.ceil(total / validatedParams.pageSize),
    });
  } catch (error) {
    console.error('Error fetching campaigns:', error);
    return NextResponse.json({ error: 'Failed to fetch campaigns' }, { status: 500 });
  }
}

// POST /api/campaigns - Create campaign
export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.organizationId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const body = await request.json();
    const validatedData = createCampaignSchema.parse(body);

    const campaign = await prisma.campaign.create({
      data: {
        ...validatedData,
        organizationId: session.user.organizationId,
        ownerId: session.user.id,
      },
    });

    return NextResponse.json(campaign, { status: 201 });
  } catch (error) {
    console.error('Error creating campaign:', error);
    if (error instanceof Error && error.name === 'ZodError') {
      return NextResponse.json({ error: 'Validation failed', details: error.message }, { status: 400 });
    }
    return NextResponse.json({ error: 'Failed to create campaign' }, { status: 500 });
  }
}