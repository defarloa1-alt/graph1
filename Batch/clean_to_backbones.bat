@echo off
REM Clean Neo4j to Backbones Only
REM Keeps: Year nodes, LCSH Subject nodes
REM Removes: Everything else (Period, Event, Person, Place, PropertyRegistry, old data)

echo.
echo ================================================================================
echo CLEAN NEO4J TO BACKBONES ONLY
echo ================================================================================
echo.
echo This will DELETE all data except:
echo   1. Year nodes (temporal backbone)
echo   2. Subject nodes with LCSH IDs (topical backbone)
echo   3. Their relationships (FOLLOWED_BY, PRECEDED_BY, BROADER_THAN)
echo.
echo WILL BE DELETED:
echo   - Period nodes
echo   - Event nodes  
echo   - Person/Human nodes
echo   - Place nodes
echo   - Organization nodes
echo   - PropertyRegistry nodes
echo   - Old Subject nodes (without lcsh_id)
echo   - All their relationships
echo.
echo ================================================================================
echo STEP 1: DRY RUN (Preview)
echo ================================================================================
echo.

python graph3-1\python\clean_to_backbones.py --dry-run

if %ERRORLEVEL% NEQ 0 goto error

echo.
echo ================================================================================
echo PREVIEW COMPLETE - Review the above to confirm what will be deleted
echo ================================================================================
echo.
set /p confirm="Type YES to proceed with deletion: "

if /i NOT "%confirm%"=="YES" (
    echo.
    echo [CANCELLED] No changes made
    goto end
)

echo.
echo ================================================================================
echo STEP 2: EXECUTE DELETION
echo ================================================================================
echo.

python graph3-1\python\clean_to_backbones.py --execute --password Chrystallum

if %ERRORLEVEL% NEQ 0 goto error

echo.
echo ================================================================================
echo [SUCCESS] DATABASE CLEANED TO BACKBONES ONLY
echo ================================================================================
echo.
echo Your Neo4j now contains:
echo   - 854 Year nodes (-753 to 100 CE)
echo   - ~400+ LCSH Subject nodes (Class D history)
echo   - Year chain relationships (FOLLOWED_BY, PRECEDED_BY)
echo   - Subject hierarchy (BROADER_THAN, if any)
echo.
echo Ready for agent subgraph generation!
echo.
goto end

:error
echo.
echo [FAILED] Cleaning failed
pause
exit /b 1

:end


