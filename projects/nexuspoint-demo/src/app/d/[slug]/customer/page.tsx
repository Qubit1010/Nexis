import RestaurantPage from '@/components/RestaurantPage';
export default function Page(p:Parameters<typeof RestaurantPage>[0]){return <RestaurantPage {...p} role="customer"/>}
