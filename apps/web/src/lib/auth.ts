import type { NextAuthOptions } from 'next-auth';

/**
 * Authentication provider configuration.
 *
 * Add a real provider (and persist organizationId in its JWT) before exposing
 * authenticated routes. An empty provider list intentionally fails closed:
 * it does not create demo users or accept unauthenticated requests.
 */
export const authOptions: NextAuthOptions = {
  providers: [],
  session: { strategy: 'jwt' },
  callbacks: {
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.sub ?? '';
        session.user.organizationId =
          typeof token.organizationId === 'string' ? token.organizationId : '';
      }
      return session;
    },
  },
};
