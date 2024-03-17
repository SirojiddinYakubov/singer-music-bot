@router.callback_query(
    PaginatedMusicsCallbackFactory.filter(F.action == "paginate"), IsAdmin()
)
async def admin_callbacks_for_music(
    callback: types.CallbackQuery,
    callback_data: PaginatedMusicsCallbackFactory,
    session: AsyncSession,
    state: FSMContext,
):
    music_id = callback_data.value
    query = select(Music).where(Music.id == music_id)
    response = await session.execute(query)
    db_music = response.scalar_one_or_none()
    if db_music:
        audio_file_id = db_music.file_id
        try:
            await callback.message.answer_audio(audio=audio_file_id)
        except Exception as e:
            await handle_error(
                f"Error sending audio in '{__file__}'\nLinenumer: {sys._getframe().f_lineno}\nException: {e}",
                e,
            )
    else:
        await callback.message.answer(_("Musiqa topilmadi!"))
    await callback.answer()