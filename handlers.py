from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import add_task_to_db, update_task_in_db, get_active_tasks, delete_task_from_db

# Определяем состояния
class TaskStates(StatesGroup):
    waiting_for_task_description = State()
    waiting_for_task_deadline = State()
    waiting_for_task_id = State()  # Новое состояние для ID задачи (редактирование)
    waiting_for_new_description = State()  # Новое состояние для нового описания
    waiting_for_new_deadline = State()  # Новое состояние для нового дедлайна
    waiting_for_task_id_deletion = State()  # Новое состояние для ID задачи (удаление)

async def start_command(message: types.Message):
    commands = """
Привет! Я твой To-Do бот. Вот список команд, которые я могу выполнять:
- /add_task: Добавить новую задачу
- /show_tasks: Показать активные задачи
- /delete_task: Удалить задачу
- /edit_task: Редактировать задачу
- /help: Показать список команд
    """
    await message.answer(commands)

# Новый обработчик для команды /help
async def help_command(message: types.Message):
    commands = """
Вот список команд, которые я могу выполнять:
- /add_task: Добавить новую задачу
- /show_tasks: Показать активные задачи
- /delete_task: Удалить задачу
- /edit_task: Редактировать задачу
- /help: Показать список команд
    """
    await message.answer(commands)

# Обработчик для добавления задачи
async def add_task(message: types.Message):
    await message.answer("Введите описание задачи:")
    await TaskStates.waiting_for_task_description.set()  # Устанавливаем состояние

async def task_description_received(message: types.Message, state: FSMContext):
    await state.update_data(task_description=message.text)  # Сохраняем описание задачи
    await message.answer("Введите дедлайн (формат ГГГГ-ММ-ДД ЧЧ:ММ):")
    await TaskStates.waiting_for_task_deadline.set()  # Переходим к ожиданию дедлайна

async def task_deadline_received(message: types.Message, state: FSMContext):
    user_data = await state.get_data()  # Получаем сохраненные данные
    task_description = user_data['task_description']  # Получаем описание задачи
    task_deadline = message.text  # Дедлайн от пользователя

    add_task_to_db(message.from_user.id, task_description, task_deadline)
    await message.answer("Задача успешно добавлена!")
    
    await state.finish()  # Завершаем состояние

# Обработчик для редактирования задачи
async def edit_task(message: types.Message):
    await message.answer("Введите ID задачи, которую хотите редактировать:")
    await TaskStates.waiting_for_task_id.set()  # Устанавливаем состояние для ожидания ID

async def task_id_received(message: types.Message, state: FSMContext):
    task_id = message.text  # Получаем ID задачи
    tasks = get_active_tasks(message.from_user.id)

    # Проверяем, существует ли задача с данным ID
    if any(task[0] == int(task_id) for task in tasks):
        await state.update_data(task_id=task_id)  # Сохраняем ID задачи
        await message.answer("Введите новое описание задачи:")
        await TaskStates.waiting_for_new_description.set()  # Устанавливаем состояние для нового описания
    else:
        await message.answer("Задача с таким ID не найдена. Пожалуйста, попробуйте еще раз.")
        await state.finish()

async def new_description_received(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    task_id = user_data['task_id']  # Получаем ID задачи
    new_description = message.text  # Новое описание задачи

    # Запрашиваем новый дедлайн
    await message.answer("Введите новый дедлайн (формат ГГГГ-ММ-ДД ЧЧ:ММ):")
    await state.update_data(new_description=new_description)  # Сохраняем новое описание
    await TaskStates.waiting_for_new_deadline.set()  # Переходим к ожиданию нового дедлайна

async def new_deadline_received(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    task_id = user_data['task_id']  # Получаем ID задачи
    new_description = user_data['new_description']  # Получаем новое описание
    new_deadline = message.text  # Новый дедлайн от пользователя

    update_task_in_db(task_id, new_description, new_deadline)

    await message.answer("Задача успешно обновлена!")
    await state.finish()  # Завершаем состояние

async def show_tasks(message: types.Message):
    tasks = get_active_tasks(message.from_user.id)
    if tasks:
        response = "Ваши активные задачи:\n"
        for task in tasks:
            response += f"ID: {task[0]}, Описание: {task[2]}, Дедлайн: {task[3]}\n"
        await message.answer(response)
    else:
        await message.answer("У вас нет активных задач.")

# Новый обработчик для удаления задачи
async def delete_task(message: types.Message):
    await message.answer("Введите ID задачи, которую хотите удалить:")
    await TaskStates.waiting_for_task_id_deletion.set()  # Устанавливаем состояние для ожидания ID для удаления

async def task_id_for_deletion_received(message: types.Message, state: FSMContext):
    task_id = message.text  # Получаем ID задачи
    tasks = get_active_tasks(message.from_user.id)

    # Проверяем, существует ли задача с данным ID
    if any(task[0] == int(task_id) for task in tasks):
        # delete_task_from_db(message.from_user.id, int(task_id))  # Удаляем задачу из БД
        delete_task_from_db(int(task_id))  # Удаляем задачу только по ID задачи

        await message.answer("Задача успешно удалена!")
    else:
        await message.answer("Задача с таким ID не найдена. Пожалуйста, попробуйте еще раз.")

    await state.finish()  # Завершаем состояние после удаления


# Регистрация команд
def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_command, commands=['start'])
    dp.register_message_handler(add_task, commands=['add_task'])
    dp.register_message_handler(task_description_received, state=TaskStates.waiting_for_task_description)
    dp.register_message_handler(task_deadline_received, state=TaskStates.waiting_for_task_deadline)
    dp.register_message_handler(show_tasks, commands=['show_tasks'])
    dp.register_message_handler(edit_task, commands=['edit_task'])
    dp.register_message_handler(task_id_received, state=TaskStates.waiting_for_task_id)
    dp.register_message_handler(new_description_received, state=TaskStates.waiting_for_new_description)
    dp.register_message_handler(new_deadline_received, state=TaskStates.waiting_for_new_deadline)
    dp.register_message_handler(delete_task, commands=['delete_task'])
    dp.register_message_handler(help_command, commands=['help'])  # Регистрация команды /help
    dp.register_message_handler(task_id_for_deletion_received, state=TaskStates.waiting_for_task_id_deletion)  # Регистрация обработчика для ID удаления
