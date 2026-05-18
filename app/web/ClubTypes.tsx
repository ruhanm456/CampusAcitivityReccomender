export interface Member {
  id: number;
  name: string;
  email: string;
  year: string;
  major: string;
}
export interface Event {
  id: number;
  club_id: number;
  title: string;
  description: string;
  created_at: string;
  updated_at: string;
}
export interface ClubData {
  id: number;
  name: string;
  description: string;
  tags: string;
  meeting_time: string;
  location: string;
  members_count: number;
  created_at: string;
  member_preview: Member[];
  is_member?: boolean;
}
