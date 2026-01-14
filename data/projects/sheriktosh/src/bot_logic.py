from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.future import select
from src.database import AsyncSessionLocal
from src.models import User

router = Router()

# FSM States
class RegState(StatesGroup):
    name = State()
    age = State()
    role = State()
    budget = State()
    district = State()

# Keyboards
role_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="I have a room"), KeyboardButton(text="I need a room")]], resize_keyboard=True)
district_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Chilonzor"), KeyboardButton(text="Yunusobod")],
    [KeyboardButton(text="Mirzo Ulugbek"), KeyboardButton(text="Yakkasaroy")]
], resize_keyboard=True)
menu_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔍 Search Roommates"), KeyboardButton(text="👤 My Profile")]], resize_keyboard=True)

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("🇺🇿 Assalomu alaykum! Welcome to SherikTosh.\nLet's set up your profile.\n\nWhat is your full name?", reply_markup=ReplyKeyboardRemove())
    await state.set_state(RegState.name)

@router.message(RegState.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Great. How old are you? (Number only)")
    await state.set_state(RegState.age)

@router.message(RegState.age)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Please enter a number.")
    await state.update_data(age=int(message.text))
    await message.answer("Are you looking for a room or offering one?", reply_markup=role_kb)
    await state.set_state(RegState.role)

@router.message(RegState.role)
async def process_role(message: Message, state: FSMContext):
    has_room = True if message.text == "I have a room" else False
    await state.update_data(has_room=has_room)
    await message.answer("What is your max budget (in $) per month?", reply_markup=ReplyKeyboardRemove())
    await state.set_state(RegState.budget)

@router.message(RegState.budget)
async def process_budget(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Please enter a number.")
    await state.update_data(budget=int(message.text))
    await message.answer("Preferred District?", reply_markup=district_kb)
    await state.set_state(RegState.district)

@router.message(RegState.district)
async def process_district(message: Message, state: FSMContext):
    data = await state.get_data()
    
    # Save to DB
    async with AsyncSessionLocal() as session:
        user = User(
            telegram_id=message.from_user.id,
            full_name=data['name'],
            age=data['age'],
            has_room=data['has_room'],
            budget_limit=data['budget'],
            district_pref=message.text,
            contact_username=message.from_user.username
        )
        await session.merge(user) # Insert or Update
        await session.commit()

    await state.clear()
    await message.answer("✅ Profile saved!", reply_markup=menu_kb)

@router.message(F.text == "🔍 Search Roommates")
async def search_handler(message: Message):
    async with AsyncSessionLocal() as session:
        # Get current user
        result = await session.execute(select(User).where(User.telegram_id == message.from_user.id))
        me = result.scalar_one_or_none()
        
        if not me:
            return await message.answer("Please /start to register first.")

        # Simple matching logic: Opposite role + Same District
        target_role = not me.has_room
        query = select(User).where(
            User.has_room == target_role,
            User.district_pref == me.district_pref,
            User.telegram_id != me.telegram_id
        ).limit(5)
        
        matches = await session.execute(query)
        results = matches.scalars().all()
        
        if not results:
            await message.answer("No matches found in your district yet. Try again later!")
        else:
            response = "🤝 **Potential Roommates:**\n\n"
            for u in results:
                response += f"👤 {u.full_name} ({u.age})\n💰 Budget: ${u.budget_limit}\n📍 {u.district_pref}\n💬 @{u.contact_username}\n\n"
            await message.answer(response)