import test from 'node:test';
import assert from 'node:assert/strict';
import { attendanceSummary,campusSlots,type Attendance } from '../src/lib/school-types.ts';
import { urgentMessage } from '../src/lib/brain.ts';
const now=new Date('2026-10-02T03:00:00Z'),settings={seeded:true,hours:[{day:5,start:480,end:810},{day:5,start:840,end:1080}]},expires='2026-10-14T12:00:00Z';
test('urgent messages retain their priority during school conversations',()=>{
 assert(urgentMessage('Attendance update: my child is unconscious'));assert(urgentMessage('بچہ بے ہوش ہے'));assert(!urgentMessage('Show sample attendance'));
});
test('campus visits respect split PKT sessions, lunch and 30-minute slots',()=>{
 const slots=campusSlots('2026-10-02',settings,[],expires,now);
 assert.equal(slots[0],'2026-10-02T03:30:00.000Z');
 assert(slots.includes('2026-10-02T08:00:00.000Z'));
 assert(!slots.includes('2026-10-02T08:30:00.000Z'));
 assert(slots.includes('2026-10-02T09:00:00.000Z'));
 assert.equal(slots.at(-1),'2026-10-02T12:30:00.000Z');
});
test('bookings and office blocks exclude every overlapping campus slot',()=>{
 const slots=campusSlots('2026-10-02',settings,[{starts_at:'2026-10-02T04:15:00Z',ends_at:'2026-10-02T05:00:00Z'}],expires,now);
 assert(!slots.includes('2026-10-02T04:00:00.000Z'));assert(!slots.includes('2026-10-02T04:30:00.000Z'));assert(slots.includes('2026-10-02T05:00:00.000Z'));
});
test('invalid dates, closed days, horizon and expiry have no invented slots',()=>{
 assert.deepEqual(campusSlots('2026-10-04',settings,[],expires,now),[]);
 assert.deepEqual(campusSlots('2026-10-32',settings,[],expires,now),[]);
 assert.deepEqual(campusSlots('2026-10-16',settings,[],expires,now),[]);
 assert.equal(campusSlots('2026-10-02',settings,[],'2026-10-02T04:00:00Z',now).length,1);
});
test('attendance counts only recorded dates and excludes excused days',()=>{
 assert.equal(attendanceSummary([]).percent,null);
 const rows=['present','late','absent','excused'].map(status=>({status})) as Attendance[];
 assert.deepEqual(attendanceSummary(rows),{recorded:4,present:2,absent:1,percent:67});
 assert.equal(attendanceSummary([{status:'excused'}] as Attendance[]).percent,null);
});
