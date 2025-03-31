import nextcord
from nextcord.ext import commands
from datetime import datetime, timedelta
import random
import openpyxl
import os
from dotenv import load_dotenv
import asyncio


intents = nextcord.Intents.default()
intents.message_content = True  # 메시지 읽기 활성화

load_dotenv(dotenv_path="C:/Users/이정연/OneDrive/바탕 화면/Bot/.env")
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

bot = commands.AutoShardedBot(command_prefix="!", intents=intents, help_command=None)

관리자_id = 1355152648914862162   # 관리자 아이디 넣기

# 봇 준비 완료 메시지 출력
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    try:
        synced = await bot.sync_application_commands()  # 슬래시 명령어 동기화
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")


@bot.slash_command(name="타임아웃", description="선택한 유저를 타임아웃합니다.", default_member_permissions=nextcord.Permissions(administrator=True))
async def timeout_user(ctx: nextcord.Interaction,
                       멤버: nextcord.Member=nextcord.SlashOption(description="멤버를 입력하세요."),
                       시간: int=nextcord.SlashOption(description="시간을 입력하세요. (분 단위)")):
    
    await ctx.response.defer()  # 응답 지연

     # ✅ 관리자 또는 서버 소유자인지 확인
    if ctx.user.guild_permissions.administrator or ctx.guild.owner_id == ctx.user.id:
        try:
            duration = timedelta(minutes=시간)  #  타임아웃 시간 설정
            await 멤버.timeout(duration, reason="타임아웃 명령어 사용")
            await ctx.followup.send(f"✅ {멤버.mention}님이 {시간}분간 타임아웃 되었습니다.")
        except Exception as e:
            await ctx.followup.send(f"❌ 타임아웃 중 오류가 발생했습니다: {e}")
    else:
        await ctx.followup.send("❌ 관리자 또는 서버 소유자만 사용할 수 있는 명령어입니다!", ephemeral=True)


@bot.slash_command(name="추방", description="유저를 추방함", default_member_permissions=nextcord.Permissions(administrator=True))
async def kick(ctx: nextcord.Interaction, 
               멤버: nextcord.Member = nextcord.SlashOption(description="추방할 멤버를 골라주세요.", required=True),
               사유: str = nextcord.SlashOption(description="사유를 적어주세요", required=False)):
    await ctx.response.defer()

    if ctx.user.guild_permissions.administrator or ctx.guild.owner_id == ctx.user.id:   # 관리자_아이디에 적힌 유저만 사용 가능
    
        if ctx.user.guild_permissions.kick_members:
            await 멤버.kick(reason=사유) # 추방코드
            await ctx.followup.send(f'✅ 추방성공 \n**사유** : {사유}')
        else:
            # 봇이 멤버를 추방할 권한이 없을 떄
            await ctx.followup.send(f"❌구성원을 추방할 권한이 없습니다.", ephemeral=True)
    else:
        # 관리자가 아닌 사람이 이 명령어를 입력하였을 때
        await ctx.followup.send(f"❌이 명령어를 사용할 권한이 없습니다.", ephemeral=True) 


@bot.slash_command(name="서버차단", description="유저를 영구차단함", default_member_permissions=nextcord.Permissions(administrator=True))
async def ban(ctx: nextcord.Interaction, 
              멤버: nextcord.Member = nextcord.SlashOption(description="서버에서 차단할 멤버를 골라주세요.", required=True),
              사유: str = nextcord.SlashOption(description="사유를 적어주세요", required=False)):
    
    await ctx.response.defer()
    
    if ctx.user.guild_permissions.administrator or ctx.guild.owner_id == ctx.user.id:  # 관리자_아이디에 적힌 유저만 사용 가능
        if ctx.user.guild_permissions.ban_members:
            await 멤버.ban(reason=사유)  # 차단코드
            await ctx.followup.send(f'✅ 차단성공 \n**사유** : {사유}')
        else:
            # 봇이 멤버를 차단할 권한이 없을 떄
            await ctx.followup.send(f"❌구성원을 차단할 수 있는 권한이 없습니다.", ephemeral=True)
    else:
        # 관리자가 아닌 사람이 이 명령어를 입력하였을 때
        await ctx.followup.send(f"❌이 명령어를 사용할 권한이 없습니다.", ephemeral=True)


@bot.slash_command(name="가입",description="가입을 할 수 있습니다.")
async def 가입(ctx: nextcord.Interaction, 닉네임: str=nextcord.SlashOption(description="닉네임은 15글자까지 가능합니다.")):
    # 엑셀 파일 경로
    excel_file = 'data.xlsx'

    try:
        # 엑셀 파일 열기 (없으면 새로 생성)
        workbook = openpyxl.load_workbook(excel_file)
    except FileNotFoundError:
        workbook = openpyxl.Workbook()

    sheet = workbook.active

    # 새로운 유저 정보 추가
    user_id = str(ctx.user.id)

    # 이미 가입되어 있는지 확인
    for row in sheet.iter_rows(values_only=True):
        if row[0] == user_id:
            await ctx.send("이미 가입되어 있습니다.")
            return
        
    if len(닉네임) > 10: # 닉네임 제한
        await ctx.send("닉네임은 최대 10글자까지만 가능합니다.")
        return

    # 가입되어 있지 않으면 가입 처리
    row = [user_id, 닉네임]
    sheet.append(row)

    # 엑셀 파일 저장
    workbook.save(excel_file)

    await ctx.send(f'✅ {닉네임}님, 가입이 완료되었습니다!')


@bot.slash_command(name="탈퇴",description="탈퇴을 할 수 있습니다.")
async def 탈퇴(ctx):

    # 엑셀 파일 경로
    excel_file = 'data.xlsx'

    try:
        # 엑셀 파일 열기
        workbook = openpyxl.load_workbook(excel_file)
        sheet = workbook.active

        # 유저의 디스코드 아이디 가져오기
        user_id = str(ctx.user.id)

        # 엑셀 파일에서 해당 유저 정보 찾기
        for idx, row in enumerate(sheet.iter_rows(min_row=1, max_row=sheet.max_row, values_only=True), start=1):
            if row[0] == user_id:
                # 해당 유저 정보를 삭제하고 저장
                sheet.delete_rows(idx)
                workbook.save(excel_file)
                await ctx.send(f"✅ 탈퇴 처리되었습니다.")
                return
        
        # 만약 해당 유저 정보가 없는 경우
        await ctx.send("가입된 정보가 없습니다.")
        
    except FileNotFoundError:
        await ctx.send("가입된 정보가 없습니다.")


@bot.slash_command(name="up지급",description="1000원을 받을 수 있습니다.")
async def 업(ctx):
    excel_file = 'data.xlsx'

    try:
        # 엑셀 파일 열기
        workbook = openpyxl.load_workbook(excel_file)
        sheet = workbook.active

        # 입력한 사용자의 아이디
        user_id = str(ctx.user.id)

        # 사용자 아이디가 있는 행 인덱스 찾기
        target_row_index = None

        # 첫 번째 열을 순회하며 사용자 아이디가 있는 행 인덱스 찾기
        for row_index in range(1, sheet.max_row + 1):
            for cell in sheet.iter_cols(min_row=row_index, max_row=row_index, min_col=1, max_col=1, values_only=True):
                if cell[0] == user_id:
                    target_row_index = row_index
                    break
            if target_row_index is not None:
                break  # 찾았으므로 더 이상 반복하지 않음

        # 사용자 아이디가 있는 행 인덱스 출력
        if target_row_index is None:
            await ctx.send("❌ 가입을 먼저 해주세요.") # 행에 아이디가 존재하지 않을 때
            return


        current_value = sheet.cell(row=target_row_index, column=3).value
        if current_value is None:
            current_value = 0
        current_value = int(current_value)

        # 새로운 값 계산
        new_value = current_value + 1000  # 기존 값에 5000을 더함

        # 값 업데이트
        sheet.cell(row=target_row_index, column=3).value = new_value

        # 엑셀 파일 저장
        workbook.save(excel_file)



        embed = nextcord.Embed(
            title=f"{ctx.user.name}",
            description=f"{ctx.user.mention}님께 1000원을 지급했습니다!",
            color=nextcord.Color(0xF3F781)
        )
        embed.add_field(name="💰 현재 잔액", value=f"{new_value}원", inline=False)
        await ctx.send(embed=embed, ephemeral=False)


    except FileNotFoundError:
        print(f"파일 '{excel_file}'을(를) 찾을 수 없습니다.")
    except Exception as e:
        print(f"에러 발생: {e}")


@bot.slash_command(name="범프지급",description="2000원을 받을 수 있습니다.")
async def 범프(ctx):
    excel_file = 'data.xlsx'

    try:
        # 엑셀 파일 열기
        workbook = openpyxl.load_workbook(excel_file)
        sheet = workbook.active

        # 입력한 사용자의 아이디
        user_id = str(ctx.user.id)

        # 사용자 아이디가 있는 행 인덱스 찾기
        target_row_index = None

        # 첫 번째 열을 순회하며 사용자 아이디가 있는 행 인덱스 찾기
        for row_index in range(1, sheet.max_row + 1):
            for cell in sheet.iter_cols(min_row=row_index, max_row=row_index, min_col=1, max_col=1, values_only=True):
                if cell[0] == user_id:
                    target_row_index = row_index
                    break
            if target_row_index is not None:
                break  # 찾았으므로 더 이상 반복하지 않음

        # 사용자 아이디가 있는 행 인덱스 출력
        if target_row_index is None:
            await ctx.send("❌ 가입을 먼저 해주세요.") # 행에 아이디가 존재하지 않을 때
            return


        current_value = sheet.cell(row=target_row_index, column=3).value
        if current_value is None:
            current_value = 0
        current_value = int(current_value)

        # 새로운 값 계산
        new_value = current_value + 2000  # 기존 값에 5000을 더함

        # 값 업데이트
        sheet.cell(row=target_row_index, column=3).value = new_value

        # 엑셀 파일 저장
        workbook.save(excel_file)



        embed = nextcord.Embed(
            title=f"{ctx.user.name}",
            description=f"{ctx.user.mention}님께 2000원을 지급했습니다!",
            color=nextcord.Color(0xF3F781)
        )
        embed.add_field(name="💰 현재 잔액", value=f"{new_value}원", inline=False)
        await ctx.send(embed=embed, ephemeral=False)


    except FileNotFoundError:
        print(f"파일 '{excel_file}'을(를) 찾을 수 없습니다.")
    except Exception as e:
        print(f"에러 발생: {e}")



@bot.slash_command(name="추천지급", description="5000원을 받을 수 있습니다.")
async def 추천(ctx):
    excel_file = 'data.xlsx'

    try:
        # 엑셀 파일 열기
        workbook = openpyxl.load_workbook(excel_file)
        sheet = workbook.active

        # 입력한 사용자의 아이디
        user_id = str(ctx.user.id)

        # 사용자 아이디가 있는 행 인덱스 찾기
        target_row_index = None

        for row_index in range(1, sheet.max_row + 1):
            cell_value = sheet.cell(row=row_index, column=1).value  
            if cell_value == user_id:
                target_row_index = row_index
                break  # 찾았으므로 중단

        # 가입이 안 되어 있는 경우
        if target_row_index is None:
            await ctx.send("❌ 가입을 먼저 해주세요.", ephemeral=True)
            return

        # 현재 잔액 가져오기
        current_value = sheet.cell(row=target_row_index, column=3).value
        if current_value is None:
            current_value = 0
        current_value = int(current_value)

        # 5000원 지급
        new_value = current_value + 5000

        # 값 업데이트
        sheet.cell(row=target_row_index, column=3).value = new_value

        # 엑셀 파일 저장
        workbook.save(excel_file)

        # ✅ 결과 메시지 출력
        embed = nextcord.Embed(
            title=f"{ctx.user.name}",
            description=f"{ctx.user.mention}님께 5000원을 지급했습니다!",
            color=nextcord.Color(0xF3F781)
        )
        embed.add_field(name="💰 현재 잔액", value=f"{new_value}원", inline=False)

        await ctx.send(embed=embed, ephemeral=False)

    except FileNotFoundError:
        await ctx.send(f"파일 '{excel_file}'을(를) 찾을 수 없습니다.")
    except Exception as e:
        await ctx.send(f"에러 발생: {e}")


@bot.slash_command(name="잔액", description="잔액을 알려줍니다.")
async def 잔액(ctx):
    excel_file = 'data.xlsx'

    try:
        # 엑셀 파일 열기
        workbook = openpyxl.load_workbook(excel_file)
        sheet = workbook.active

        # 입력한 사용자의 아이디
        user_id = str(ctx.user.id)

        # 사용자 아이디가 있는 행 인덱스 찾기
        target_row_index = None

        # 첫 번째 열을 순회하며 사용자 아이디가 있는 행 인덱스 찾기
        for row_index in range(1, sheet.max_row + 1):
            for cell in sheet.iter_cols(min_row=row_index, max_row=row_index, min_col=1, max_col=1, values_only=True):
                if cell[0] == user_id:
                    target_row_index = row_index
                    break
            if target_row_index is not None:
                break  # 찾았으므로 더 이상 반복하지 않음

        # 사용자 아이디가 있는 행 인덱스 출력
        if target_row_index is None:
            await ctx.send("가입을 해주세요.")
            return

        current_value = sheet.cell(row=target_row_index, column=3).value

        current_value = int(current_value)


        # 엑셀 파일 저장
        workbook.save(excel_file)
        embed = nextcord.Embed(
            title=f'{ctx.user.name}',           # 제목과 설명은 임베드에 1개만 추가가 가능합니다
            description='돈 잔액',
            color=nextcord.Color(0xF3F781)  # 색상 코드
        )
        embed.add_field(name='현재 잔액', value=f'{current_value}', inline=False) # 필드
        
        
        await ctx.send(embed=embed, ephemeral=False)


    except FileNotFoundError:
        print(f"파일 '{excel_file}'을(를) 찾을 수 없습니다.")
    except Exception as e:
        print(f"에러 발생: {e}")



@bot.slash_command(name="잔액변경", description="유저의 잔액을 변경할 수 있습니다.", default_member_permissions=nextcord.Permissions(administrator=True))
async def 잔액변경(ctx, 
              유저: nextcord.Member = nextcord.SlashOption(description="유저아이디를 입력하세요"), 
              변경할금액: int = nextcord.SlashOption(description="변경할 금액을 입력하세요.")):

    if ctx.user.guild_permissions.administrator or ctx.guild.owner_id == ctx.user.id:
        excel_file = 'data.xlsx'

        try:
            # 엑셀 파일 열기
            workbook = openpyxl.load_workbook(excel_file)
            sheet = workbook.active

            # 입력한 사용자의 아이디
            user_id = str(유저.id)

            # 사용자 아이디가 있는 행 인덱스 찾기
            target_row_index = None

            for row_index in range(1, sheet.max_row + 1):
                cell_value = sheet.cell(row=row_index, column=1).value  
                if cell_value == user_id:
                    target_row_index = row_index
                    break  # 찾았으므로 중단

            # 사용자 아이디가 없을 경우
            if target_row_index is None:
                await ctx.send("❌ 가입이 되어있지 않거나 존재하지 않는 유저입니다.", ephemeral=True)
                return

            # 현재 잔액 가져오기
            current_value = sheet.cell(row=target_row_index, column=3).value
            if current_value is None:
                current_value = 0
            current_value = int(current_value)

            # 새로운 값 계산
            new_value = current_value + 변경할금액  # 잔액 변경

            # 값 업데이트
            sheet.cell(row=target_row_index, column=3).value = new_value

            # 엑셀 파일 저장
            workbook.save(excel_file)

            # ✅ 변경된 잔액을 임베드로 출력
            embed = nextcord.Embed(
                title=f'{ctx.user.name}님의 요청',
                description=f'{유저.mention}님의 잔액 변경 완료!',
                color=nextcord.Color(0xF3F781)  
            )
            embed.add_field(name='변경한 금액', value=f'{변경할금액}원', inline=False)  
            embed.add_field(name='현재 잔액', value=f'{new_value}원', inline=False)  

            await ctx.send(embed=embed, ephemeral=False)

        except FileNotFoundError:
            await ctx.send("❌ 파일을 찾을 수 없습니다. `data.xlsx` 파일이 있는지 확인하세요!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ 오류 발생: {e}", ephemeral=True)


@bot.slash_command(name="메시지삭제", description="입력한 개수만큼 메시지를 삭제합니다.", default_member_permissions=nextcord.Permissions(administrator=True))
async def delete_messages(
    ctx: nextcord.Interaction,
    개수: int = nextcord.SlashOption(description="삭제할 메시지 개수를 입력하세요.", min_value=1, max_value=100)
):
    await ctx.response.defer()  # 응답 지연 방지

    if not ctx.guild.me.guild_permissions.manage_messages:
        return await ctx.followup.send("❌ 봇에게 '메시지 관리' 권한이 없습니다. 서버 설정을 확인하세요.")

    if ctx.user.guild_permissions.administrator or ctx.guild.owner_id == ctx.user.id:
        try:
            deleted = await ctx.channel.purge(limit=개수)
            await ctx.followup.send(f"✅ 최근 {len(deleted)}개의 메시지를 삭제했습니다.", ephemeral=True)
        except nextcord.Forbidden:
            await ctx.followup.send("❌ 메시지 삭제 권한이 부족합니다.")
        except Exception as e:
            await ctx.followup.send(f"❌ 메시지 삭제 중 오류가 발생했습니다.: {e}")
    else:
        await ctx.followup.send("❌ 관리자만 사용할 수 있는 명령어입니다.", ephemeral=True)


@bot.command(name="닉네임변경")
async def 닉네임변경(ctx, *, 새_닉네임: str):
    # ✅ 봇이 닉네임 변경 권한을 가지고 있는지 확인
    if not ctx.guild.me.guild_permissions.manage_nicknames:
        return await ctx.send("❌ 봇에게 '닉네임 변경' 권한이 없습니다. 서버 설정을 확인하세요.")

    try:
        await ctx.author.edit(nick=새_닉네임)
        await ctx.send(f"✅ {ctx.author.mention}님의 닉네임이 `{새_닉네임}`(으)로 변경되었습니다.")
    except nextcord.Forbidden:
        await ctx.send("❌ 닉네임 변경 권한이 부족합니다.")
    except Exception as e:
        await ctx.send(f"❌ 닉네임 변경 중 오류가 발생했습니다: {e}")


@bot.command(name="치우")  
async def 치우(ctx):
    await ctx.send("서버 내 최고 알파메일") 

@bot.command(name="디카프리오")  
async def 디카프리오(ctx):
    await ctx.send('서버 내 핵폭탄급 존재감')  
    
@bot.command(name="수빈")  
async def 수빈(ctx):
    await ctx.send("서버 내 최강 미녀") 

@bot.command(name="인천나얼")  
async def 인천나얼(ctx):
    await ctx.send("서버 내 핵심인재") 

@bot.command(name="봄")  
async def 봄(ctx):
    await ctx.send('봄이는 수비니를 조아해')  

@bot.command(name="어서오세요") # 명령
async def 어서오세요(ctx):
    ran = random.randint(0,3)  # 랜덤으로 보낼 답변의 갯수
    if ran == 0:         
        r = "반가워요"  
    if ran == 1:  
        r = "환영해요"  
    if ran == 2:
        r = "음챗해요"
    if ran == 3:
        r = "게임해요"
    await ctx.channel.send(r)  # 변수 r의 값을 보냄

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    print("등록된 명령어 목록:", [cmd.name for cmd in bot.commands])

bot.run(TOKEN) #토큰
